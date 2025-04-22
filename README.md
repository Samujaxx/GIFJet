# GIFjet 🎞️✈️

**GIFjet** is a sleek Windows widget that lets you search, preview, and pin GIFs from Giphy directly to your desktop.

---

## ✨ Features
- 🖼️ Frameless GIF widget with transparent background
- 🔍 Search GIFs via Giphy
- ⭐ Save favorite GIFs
- 🎨 Dark mode with color accents
- 🖱️ Drag & resize support
- ⛩️ Tray menu with quick actions
- 🔄 Optional autostart on Windows boot

---

## How to Set Up the Project

### Requirements

- Python 3.8 or higher
- PyQt6
- aiohttp
- PyInstaller (if you want to create your own `.exe` file)

### 1. Install Dependencies
Run the following command to install the required dependencies:

```
pip install -r requirements.txt
```

### 2. Use Inno Setup to Create the Installer

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php).
2. Open the provided `GIFjet.iss` script in Inno Setup.
3. Modify the paths if necessary to match your directory structure.
4. Compile the script to generate the `setup.exe` installer.

### 3. (Optional) Create a PyInstaller Executable

If you prefer to create your own `.exe` file from the source code, follow these steps:

1. Install PyInstaller:

```
pip install pyinstaller
```

2. Navigate to the directory containing the source code and run PyInstaller:

```
pyinstaller --onefile GIFjet.py
```

3. After the build process completes, you can find the `.exe` in the `dist/` folder.

---

Now you can either use the `setup.exe` installer or run the executable directly from the `dist/` folder.

## 💡 Notes

- The widget starts in the background (tray icon).
- Settings and favorites are saved persistently in `config/`.
- You can enable/disable autostart anytime via the tray menu.

---

## 📝 License

MIT License — see [`LICENSE`](LICENSE) for full terms.

---

Created with ❤️ by Samujaxx — Powered by Giphy 🚀