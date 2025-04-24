
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

## 🛠️ How to Set Up Widget

### 1. Download & Install (For Regular Users)

For those who want an easy setup, just download the `setup.exe` and follow the installation process.

1. Download the [GIFjet Setup](https://github.com/Samujaxx/GIFJet/releases)
2. Run the installer.
3. Follow the instructions in the installer to complete the installation process.

Once installed, you can launch GIFjet directly from the Start Menu or desktop shortcut.

## 💡 Notes

- The widget starts in the background (tray icon).
- Settings and favorites are saved persistently in `config/`.
- You can enable/disable autostart anytime via the tray menu.

---

## 🛠️ How to Set Up the project (For Nerds 🔧)

### 1. Requirements 

- Python 3.8 or higher
- PyQt6
- aiohttp
- PyInstaller (if you want to create your own `.exe` file)

### 2. Install Dependencies

If you're working with the source code, first install the required dependencies:

```bash
pip install -r requirements.txt
```

---

### 3. Use Inno Setup to Create the Installer

If you want to create your own installer using **Inno Setup**, follow these steps:

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php).
2. Open the provided `GIFjet.iss` script in Inno Setup.
3. Modify the paths in the `.iss` script if necessary to match your directory structure.
4. Compile the script to generate the `setup.exe` installer.

---

### 4. (Optional) Create a PyInstaller Executable

Alternatively, you can create your own `.exe` file directly from the source code:

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Navigate to the directory containing the source code and run PyInstaller:

```bash
pyinstaller --onefile GIFjet.py
```

3. After the build process completes, you can find the `.exe` in the `dist/` folder.

---

Now you can either use the `setup.exe` installer or run the executable directly from the `dist/` folder.


## 📝 License

MIT License — see [`LICENSE`](LICENSE) for full terms.

---

Created with ❤️ by Samujaxx — Powered by Giphy 🚀
