'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');

const PORT = Number(process.env.PORT) || 8421;
const BIND = process.env.BIND || '0.0.0.0';

const ROOT = path.join(__dirname, '..', '..');
const INDEX = '/military-gun-game/index.html';

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json',
  '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.css': 'text/css; charset=utf-8', '.ico': 'image/x-icon', '.map': 'application/json'
};


const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);

  if (p === '/' || p === '') { res.writeHead(302, { Location: INDEX }); res.end(); return; }
  const f = path.normalize(path.join(ROOT, p));
  if (!f.startsWith(ROOT)) { res.writeHead(403); res.end('forbidden'); return; }
  fs.readFile(f, (e, d) => {
    if (e) { res.writeHead(404, { 'Content-Type': 'text/plain' }); res.end('not found'); return; }
    res.writeHead(200, {
      'Content-Type': TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream',
      'Cache-Control': 'no-cache'
    });
    res.end(d);
  });
});


const GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';
const acceptKey = key => crypto.createHash('sha1').update(key + GUID).digest('base64');

function wsSend(sock, opcode, payload) {
  if (sock.destroyed || !sock.writable) return;
  const len = payload.length;
  let head;
  if (len < 126) {
    head = Buffer.alloc(2);
    head[1] = len;
  } else if (len < 65536) {
    head = Buffer.alloc(4);
    head[1] = 126;
    head.writeUInt16BE(len, 2);
  } else {
    head = Buffer.alloc(10);
    head[1] = 127;
    head.writeBigUInt64BE(BigInt(len), 2);
  }
  head[0] = 0x80 | opcode;
  try { sock.write(Buffer.concat([head, payload])); } catch (e) { sock.destroy(); }
}
const sendJSON = (sock, obj) => wsSend(sock, 0x1, Buffer.from(JSON.stringify(obj)));



let nextId = 1;
const clients = new Map();      
let hostId = null;
let hostLastBeat = 0;           
let lastWave = 1;
let lastEnemies = [];           

const peerList = () => [...clients.values()].map(c => ({ id: c.id, name: c.name }));
const sanitizeName = v => String(v || 'OPERATOR').replace(/[^\w \-.]/g, '').slice(0, 14) || 'OPERATOR';

function broadcast(obj, exceptId) {
  const data = JSON.stringify(obj);
  for (const c of clients.values()) {
    if (c.id === exceptId) continue;
    wsSend(c.sock, 0x1, Buffer.from(data));
  }
}
const toHost = obj => { const h = clients.get(hostId); if (h) sendJSON(h.sock, obj); };
const toClient = (id, obj) => { const c = clients.get(id); if (c) sendJSON(c.sock, obj); };
const setHost = id => {
  hostId = id;
  broadcast({ t: 'host', id });
  log(`host is now ${clients.get(id) ? clients.get(id).name : 'nobody'}`);
};


function claimHost(id) {
  if (id === hostId) return;
  const silent = Date.now() - hostLastBeat > 2500;
  if (!hostId || !clients.has(hostId) || silent) {
    hostLastBeat = Date.now();
    lastEnemies = [];
    setHost(id);
  }
}

function handleMessage(c, msg) {
  if (!msg || typeof msg.t !== 'string') return;
  switch (msg.t) {
    case 'join': {
      c.name = sanitizeName(msg.name);
      c.token = String(msg.token || '').slice(0, 40);
     
      if (c.token) {
        for (const other of clients.values()) {
          if (other !== c && other.token === c.token) other.sock.destroy();
        }
      }
      sendJSON(c.sock, {
        t: 'welcome', id: c.id, host: hostId, p: peerList().filter(p => p.id !== c.id),
        e: lastEnemies, w: lastWave
      });
      broadcast({ t: 'join', id: c.id, n: c.name }, c.id);
      log(`${c.name} joined (${clients.size} online)`);
      break;
    }
    case 'claim':
      if (msg.name) {
        const n = sanitizeName(msg.name);
        if (n !== c.name) { c.name = n; broadcast({ t: 'name', id: c.id, n }); }
      }
      claimHost(c.id);
      break;
    case 'name': {
      const n = sanitizeName(msg.name);
      if (n !== c.name) { c.name = n; broadcast({ t: 'name', id: c.id, n }); }
      break;
    }
    case 'pos':
   
      broadcast(Object.assign({ t: 'pos', id: c.id, n: c.name }, msg, { t: 'pos' }), c.id);
      break;
    case 'es':
      if (c.id !== hostId) return;
      hostLastBeat = Date.now();
      lastEnemies = Array.isArray(msg.l) ? msg.l : [];
      lastWave = msg.w | 0;
      broadcast({ t: 'es', w: lastWave, l: lastEnemies, f: msg.f || [] }, c.id);
      break;
    case 'hit':

      if (c.id === hostId) return;
      toHost({ t: 'hit', e: msg.e, d: msg.d, h: msg.h ? 1 : 0, id: c.id });
      break;
    case 'hurt':
      if (c.id !== hostId) return;
      toClient(msg.id, { t: 'hurt', d: msg.d });
      break;
    case 'shoot':
    case 'boom':
    case 'dead':
    case 'alive':
      broadcast(Object.assign({}, msg, { id: c.id }), c.id);
      break;
    case 'ping':
      sendJSON(c.sock, { t: 'pong', c: msg.c });
      break;
  }
}

function handleSocket(sock) {
  const client = { id: 0, name: 'OPERATOR', sock, token: '', lastSeen: Date.now() };
  let joined = false;
  let buf = Buffer.alloc(0);
  let frag = null, fragOp = 0;

  const close = () => {
    if (!joined) return;
    joined = false;
    clients.delete(client.id);
    broadcast({ t: 'leave', id: client.id });
    log(`${client.name} left (${clients.size} online)`);
    if (hostId === client.id) {
      const next = clients.keys().next();
      setHost(next.done ? null : next.value);
    }
  };

  sock.on('data', chunk => {
    client.lastSeen = Date.now();
    buf = Buffer.concat([buf, chunk]);
    while (buf.length >= 2) {
      const b0 = buf[0], b1 = buf[1];
      const fin = (b0 & 0x80) !== 0, op = b0 & 0x0f;
      const masked = (b1 & 0x80) !== 0;
      let len = b1 & 0x7f, off = 2;
      if (len === 126) {
        if (buf.length < 4) return;
        len = buf.readUInt16BE(2); off = 4;
      } else if (len === 127) {
        if (buf.length < 10) return;
        len = Number(buf.readBigUInt64BE(2)); off = 10;
      }
      const maskOff = off;
      if (masked) off += 4;
      if (buf.length < off + len) return;
      let payload = buf.subarray(off, off + len);
      if (masked) {
        const m = buf.subarray(maskOff, maskOff + 4);
        const out = Buffer.alloc(len);
        for (let i = 0; i < len; i++) out[i] = payload[i] ^ m[i & 3];
        payload = out;
      }
      buf = buf.subarray(off + len);

      if (op === 0x8) { wsSend(sock, 0x8, Buffer.alloc(0)); sock.end(); return; }
      if (op === 0x9) { wsSend(sock, 0xA, payload); continue; }
      if (op === 0xA) continue;
      if (op === 0x1 || op === 0x2) {
        if (!fin) { frag = payload; fragOp = op; continue; }
        handleFrame(payload);
      } else if (op === 0x0 && frag) {
        frag = Buffer.concat([frag, payload]);
        if (fin) { handleFrame(frag); frag = null; }
      }
    }
  });

  function handleFrame(payload) {
    let msg;
    try { msg = JSON.parse(payload.toString()); } catch (e) { return; }
    if (!joined) {
      if (msg.t !== 'join') return;
      joined = true;
      client.id = nextId++;
      clients.set(client.id, client);
    }
    handleMessage(client, msg);
  }

  sock.on('close', close);
  sock.on('error', () => { try { sock.destroy(); } catch (e) {} close(); });
}

server.on('upgrade', (req, sock) => {
  const key = req.headers['sec-websocket-key'];
  if ((req.headers.upgrade || '').toLowerCase() !== 'websocket' || !key) { sock.destroy(); return; }
  sock.write(
    'HTTP/1.1 101 Switching Protocols\r\n' +
    'Upgrade: websocket\r\n' +
    'Connection: Upgrade\r\n' +
    'Sec-WebSocket-Accept: ' + acceptKey(key) + '\r\n\r\n'
  );
  sock.setNoDelay(true);
  handleSocket(sock);
});

setInterval(() => {
  const now = Date.now();
  for (const c of clients.values()) {
    if (c.sock.destroyed) continue;
    if (now - c.lastSeen > 45000) { c.sock.destroy(); continue; }
    wsSend(c.sock, 0x9, Buffer.alloc(0));
  }
}, 20000).unref();


function log(msg) { console.log('[' + new Date().toISOString().slice(11, 19) + '] ' + msg); }

function lanAddresses() {
  const out = [];
  for (const list of Object.values(os.networkInterfaces())) {
    for (const a of list || []) {
      if (a.family === 'IPv4' && !a.internal) out.push(a.address);
    }
  }
  return out;
}

server.listen(PORT, BIND, () => {
  log('OPERATION BLACKOUT 3D — CO-OP SERVER');
  log('local    http://localhost:' + PORT);
  for (const ip of lanAddresses()) log('LAN      http://' + ip + ':' + PORT);
  log('join from any of those addresses; /ws carries the co-op session');
});
