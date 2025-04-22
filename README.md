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

## 📦 Installation Methods

### 1. 🔧 **Install via Installer (Recommended)**
- Navigate to the `Installer/Installer/` folder.
- Run `GIFjetSetup.exe` to install GIFjet like a regular Windows app.
- Includes system tray access, auto-start toggle, and theme customization.

---

### 2. 🐍 **Run from Source with PyInstaller**
#### Prerequisites:
- Python 3.10+
- `pip install -r requirements.txt` (or see below for manual list)

#### Steps:
```bash
# Clone the repository
git clone https://github.com/Samujaxx/GIFjet.git
cd GIFjet

# Install dependencies
pip install -r requirements.txt

# Build the executable
pyinstaller --noconfirm GIFjet.spec
```

- The `.exe` will appear in the `dist/` folder.
- Double-click `GIFjet.exe` to launch the widget.

---

### 3. 📦 **Build a Custom Installer with Inno Setup**
#### Prerequisites:
- [Inno Setup 6.4+](https://jrsoftware.org/isinfo.php)

#### Steps:
```bash
# Navigate to the Installer folder
cd Installer

# Open the installer script in Inno Setup
start GIFjetInstaller.iss
```

- Compile the script with the Inno Setup IDE.
- The installer output will be in `Installer/Installer/`.

---

## 📁 Folder Structure

```
├── assets/          # Icons, header image, loading spinners
├── config/          # User data: favorites, settings
├── dist/            # PyInstaller output (.exe)
├── Installer/       
│   ├── Installer/   # Output of the Inno Setup compiler
│   └── GIFjetInstaller.iss  # Inno Setup script
├── src/             # Application source code
│   ├── main.py
│   ├── giphy.py
│   ├── utils.py
│   ├── theme.py
│   └── giphySearchDialog.py
├── style.qss        # Stylesheet (dark mode, themes)
├── GIFjet.spec      # PyInstaller config
└── README.md
```

---

## 🧩 Requirements

If you're not using `requirements.txt`, install manually:
```bash
pip install PyQt6 PyQt6-WebEngine qasync requests portalocker
```

---

## 💡 Notes

- The widget starts in the background (tray icon).
- Settings and favorites are saved persistently in `config/`.
- You can enable/disable autostart anytime via the tray menu.

---

## 📝 License

MIT License — see [`LICENSE`](LICENSE) for full terms.

---

Created with ❤️ by Samujaxx — Powered by Giphy 🚀