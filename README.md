# 🎖️ Military Game

A browser-based military game available in **two versions**: a full **3D experience** with Blender-made models, and a lightweight **2D version**. No installation of a game engine is needed, just a local web server and a modern browser.

---

## 🎮 Game Versions

| Version | File | Description |
|---------|------|-------------|
| **3D** | `index.html` | Full 3D game using models and assets created in Blender |
| **2D** | `game2d.html` | Lightweight top-down / 2D version, runs on low-end devices |

---

## 📁 Project Structure

```
.
├── index.html        # 3D version of the game (Blender models)
├── game2d.html       # 2D version of the game
├── serve.cjs         # Local Node.js static file server
├── serve.log         # Server output / request log (auto-generated)
├── build/            # Build assets (models, textures, sounds, scripts)
└── README.md         # You are here
```

> Note: rename `build/` above if your assets folder has a different name.

---

## 🚀 Getting Started

### Requirements

- [Node.js](https://nodejs.org/) v16 or newer
- A modern browser (Chrome, Edge, Firefox) with WebGL support for the 3D version

### Run the game

1. Open a terminal in the project folder.
2. Start the local server:

   ```bash
   node serve.cjs
   ```

3. Open your browser and visit the address shown in the terminal (usually `http://localhost:3000`, check `serve.cjs` for the exact port):

   - **3D version:** `http://localhost:3000/index.html`
   - **2D version:** `http://localhost:3000/game2d.html`

> ⚠️ Open the game through the server, not by double-clicking the HTML files. Loading 3D models and assets directly from `file://` is blocked by browsers (CORS).

---

## 🧱 Build Assets

The `build/` folder contains everything the game loads at runtime:

- **3D models**: created in Blender and exported (e.g. `.glb` / `.gltf`)
- **Textures & materials**
- **Audio**: sound effects and music
- **Scripts / bundles**: compiled game code

If you edit a model in Blender, re-export it to the same file name and path in `build/`, then refresh the browser (use `Ctrl + Shift + R` to bypass cache).

---

## 🛠️ Blender Workflow

1. Open or create the model in Blender.
2. Apply transforms (`Ctrl + A`) and check the scale and orientation.
3. Export as **glTF 2.0 (.glb)**.
4. Place the exported file inside `build/`.
5. Reload `index.html` to see the changes.

---

## 🪵 Logs

`serve.log` records server activity such as requests and errors. If something fails to load (missing model, 404, wrong path), check this file first.

To watch the log live:

```bash
tail -f serve.log
```

---

## 🕹️ Controls

> Update this section to match your game.

| Action | Key |
|--------|-----|
| Move | `W` `A` `S` `D` |
| Aim | Mouse |
| Shoot | Left Click |
| Reload | `R` |
| Pause | `Esc` |

---

## 🐞 Troubleshooting

- **Blank screen / models missing:** make sure you started `serve.cjs` and are not opening the file directly.
- **Port already in use:** close the other process or change the port in `serve.cjs`.
- **3D version is slow:** use `game2d.html`, or enable hardware acceleration in your browser.
- **Changes not showing:** hard refresh with `Ctrl + Shift + R`.

---

## 🗺️ Roadmap

- [ ] More missions and levels
- [ ] New weapons and vehicles
- [ ] Multiplayer support
- [ ] Mobile touch controls

---

## 📄 License

Add your license here (e.g. MIT). Models and assets created in Blender are © the project author unless stated otherwise.

---

## 🙌 Credits

- Game design & development: *your name*
- 3D models: made in [Blender](https://www.blender.org/)
