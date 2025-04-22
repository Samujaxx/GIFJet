
import os
import sys
import json
import requests
import tempfile
import socket
import base64
import threading
import portalocker
import winreg
import webbrowser
from utils import resourcePath
from giphy import searchGiphy
from theme import loadStyleWithAccent
from giphySearchDialog import GiphySearchDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QSize, QRect, QPoint ,QUrl, QTimer, QEvent
from PyQt6.QtGui import QMovie, QPixmap, QIcon, QAction
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QMenu, QFileDialog, QSystemTrayIcon, QStyle, QInputDialog, QVBoxLayout, QDialog, QScrollArea, QHBoxLayout, QMessageBox, QPushButton, QCheckBox, QWidgetAction

PORT = 65432

EDGE_MARGIN = 8

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"

def isAlreadyRunning():
    lockfile = os.path.join(tempfile.gettempdir(), 'gifjet.lock')
    global lockhandle
    lockhandle = open(lockfile, 'w')
    try:
        portalocker.lock(lockhandle, portalocker.LOCK_EX | portalocker.LOCK_NB)
        return False
    except portalocker.exceptions.LockException:
        return True
    
def trySignalExistingInstance():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", PORT))
            s.sendall(b"restore")
            return True
    except:
        return False

class ClickableGifPreview(QLabel):
    def __init__(self, gifUrl, clickCallback):
        super().__init__()
        self.gifUrl = gifUrl
        self.clickCallback = clickCallback

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clickCallback(self.gifUrl)

class GifWidget(QWidget):
    def __init__(self, gifPath):
        super().__init__()
        self.dragPosition = None
        self.setWindowTitle("GIF Widget")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.giphykey = "mFhemUovCSMzp6qXKbPXM4J56FhOMvCr"

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMouseTracking(True)
        self.setMouseTracking(True)

        self.loadSettings()

        if not self.loadLastUsedGif():
            self.loadGifFromFile(gifPath)

        self.createTrayIcon()
        self.show()
    
    def isAutoStartEnabled(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, "GIFjet")
            return True
        except FileNotFoundError:
            return False

    def setAutoStart(self, enable):
        run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_path = f'"{os.path.abspath(sys.argv[0])}"'

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE)
        except FileNotFoundError:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, run_key)

        if enable:
            winreg.SetValueEx(key, "GIFjet", 0, winreg.REG_SZ, app_path)
        else:
            try:
                winreg.DeleteValue(key, "GIFjet")
            except FileNotFoundError:
                pass
    
    def createTrayIcon(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(resourcePath("assets/icon.ico")))
        trayMenu = QMenu()

        if not hasattr(self, "settings"):
            self.loadSettings()

        trayMenu.addAction(QAction("Choose from Local Files", self, triggered=self.loadLocalGif))
        trayMenu.addAction(QAction("Search from Giphy", self, triggered=self.searchGiphyAndLoad))
        trayMenu.addSeparator()

        colorMenu = QMenu("Change Accent Color", self)
        for name in ["Red", "Blue", "Purple", "Green", "Pink"]:
            action = QAction(name, self)
            action.triggered.connect(lambda _, c=name.lower(): self.setAccentColor(c))
            colorMenu.addAction(action)
        trayMenu.addMenu(colorMenu)

        trayMenu.addSeparator()

        self.showMinimizeMessageAction = QAction("Show Tray Message on Minimize", self)
        self.showMinimizeMessageAction.setCheckable(True)
        self.showMinimizeMessageAction.setChecked(self.settings.get("showTrayMessage", True))
        self.showMinimizeMessageAction.toggled.connect(self.saveSettings)
        trayMenu.addAction(self.showMinimizeMessageAction)

        self.autoStartAction = QAction("Start with Windows", self)
        self.autoStartAction.setCheckable(True)
        self.autoStartAction.setChecked(self.isAutoStartEnabled())
        self.autoStartAction.toggled.connect(self.setAutoStart)
        trayMenu.addAction(self.autoStartAction)

        trayMenu.addSeparator()
        trayMenu.addAction(QAction("Restore", self, triggered=self.showNormal))
        minimizeAction = QAction("Minimize", self)
        minimizeAction.triggered.connect(self.minimizeToTray)
        trayMenu.addAction(minimizeAction)
        trayMenu.addAction(QAction("Exit", self, triggered=QApplication.quit))

        # Add Powered by Giphy GIF
        trayMenu.addSeparator()
        self.addPoweredByGiphyToMenu(trayMenu)

        self.tray.setContextMenu(trayMenu)
        self.tray.activated.connect(self.onTrayIconActivated)
        self.tray.show()
    
    
    def openGiphyWebsite(self):
        """ Open the Giphy website in a browser when triggered. """
        webbrowser.open("https://giphy.com/")
    
    def addPoweredByGiphyToMenu(self, trayMenu):
        # Create a widget to hold the GIF
        widget = QWidget()
        layout = QVBoxLayout()

        # Create a QLabel to hold the GIF and set the GIF to it
        label = QLabel()
        movie = QMovie(resourcePath("assets/PoweredBy_200_Horizontal_Light-Backgrounds_With_Logo.gif"))  # Path to your GIF
        label.setMovie(movie)
        movie.start()

        # Add the QLabel to the layout
        layout.addWidget(label)
        widget.setLayout(layout)

        # Create a QWidgetAction and add the widget to the menu
        powered_by_action = QWidgetAction(self)
        powered_by_action.setDefaultWidget(widget)
        powered_by_action.triggered.connect(self.openGiphyWebsite)
        trayMenu.addAction(powered_by_action)
    
    
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()

    def toggleTrayMessageOption(self, checked):
        self.settings["suppressTrayMessage"] = checked
        self.saveSettings()
    
    def minimizeToTray(self):
        self.hide()
        if self.settings.get("showTrayMessage", True):
            self.tray.showMessage(
                "GIF Widget",
                "Minimized to tray. Right-click the tray icon to restore or exit.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
            
    def setAccentColor(self, colorName):
        colorMap = {
            "red": "#e50914",
            "blue": "#1e90ff",
            "green": "#00c853",
            "purple": "#9c27b0",
            "pink": "#ff69b4"
        }
        accent = colorMap.get(colorName.lower(), "#e50914")
        QApplication.instance().setStyleSheet(loadStyleWithAccent(accent))

        os.makedirs(resourcePath("config"), exist_ok=True)
        with open(resourcePath("config/settings.json"), "w") as f:
            json.dump({"accent": accent}, f)

    def loadSettings(self):
        self.settings = {}
        try:
            if os.path.exists(resourcePath("config/settings.json")):
                with open(resourcePath("config/settings.json"), "r") as f:
                    self.settings = json.load(f)
        except:
            self.settings = {}

    def saveSettings(self):
        os.makedirs(resourcePath("config"), exist_ok=True)
        self.settings["showTrayMessage"] = self.showMinimizeMessageAction.isChecked()
        with open(resourcePath("config/settings.json"), "w") as f:
            json.dump(self.settings, f)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.resizing = self.getResizeDirection(event.pos())
            if self.resizing:
                self.resizeOrigin = event.globalPosition().toPoint()
                self.originalSize = self.size()
            else:
                self.dragPosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.resizing and hasattr(self, "resizeOrigin"):
                self.performResize(event.globalPosition().toPoint())
            elif self.dragPosition:
                newPos = event.globalPosition().toPoint() - self.dragPosition
                self.move(newPos)
            event.accept()
        else:
            self.setCursorShape(event.pos())

    def mouseReleaseEvent(self, event):
        self.dragPosition = None
        self.resizeOrigin = None
        self.resizing = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def getResizeDirection(self, pos):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        if x >= w - EDGE_MARGIN and y >= h - EDGE_MARGIN:
            return "bottomright"
        return None

    def setCursorShape(self, pos):
        if self.getResizeDirection(pos) == "bottomright":
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def performResize(self, globalPos):
        offset = globalPos - self.resizeOrigin
        dx = offset.x()
        dy = offset.y()
        new_width = self.originalSize.width() + dx
        new_height = self.originalSize.height() + dy
        width_from_height = int(new_height * self.aspectRatio)
        height_from_width = int(new_width / self.aspectRatio)
        if width_from_height <= new_width:
            final_width = width_from_height
            final_height = new_height
        else:
            final_width = new_width
            final_height = height_from_width
        final_width = max(final_width, 100)
        final_height = max(final_height, 100)
        self.resize(final_width, final_height)
        self.label.resize(self.size())
        self.movie.setScaledSize(self.size())

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        loadOwnGif = menu.addAction("Choose from local files")
        searchOnline = menu.addAction("Search from Giphy")
        minimizeWindow = menu.addAction("Minimize")
        exitWidget = menu.addAction("Exit")
        action = menu.exec(event.globalPos())
        if action == loadOwnGif:
            self.loadLocalGif()
        elif action == searchOnline:
            self.searchGiphyAndLoad()
        elif action == minimizeWindow:
            self.minimizeToTray()
        elif action == exitWidget:
            QApplication.quit()

    def scaleToFit(self, originalSize: QSize, maxSize: QSize) -> QSize:
        ow, oh = originalSize.width(), originalSize.height()
        mw, mh = maxSize.width(), maxSize.height()
        widthRatio = mw / ow
        heightRatio = mh / oh
        scaleFactor = min(widthRatio, heightRatio, 1)
        return QSize(int(ow * scaleFactor), int(oh * scaleFactor))

    def onFirstFrame(self, frameNumber):
        if frameNumber == 0:
            originalSize = self.movie.frameRect().size()
            maxSize = QSize(600, 600)
            scaledSize = self.scaleToFit(originalSize, maxSize)
            self.aspectRatio = scaledSize.width() / scaledSize.height()
            self.resize(scaledSize)
            self.label.resize(scaledSize)
            self.movie.setScaledSize(scaledSize)
            self.movie.frameChanged.disconnect(self.onFirstFrame)

    def onGifPreviewClicked(self, gifUrl, dialog):
        self.loadGifFromUrl(gifUrl)
        dialog.accept()

    def loadLocalGif(self):
        """Handles loading a local GIF file."""
        filePath, _ = QFileDialog.getOpenFileName(self, "Select a GIF", "", "GIF Files (*.gif);;All Files (*)")
        if filePath:
            try:
                # Stop any previous movie and clear it
                if hasattr(self, 'movie') and self.movie:
                    self.movie.stop()
                    del self.movie  # Remove the previous movie instance

                # Load and play the local GIF
                self.movie = QMovie(filePath)
                self.label.setMovie(self.movie)  # Set the movie to the label for displaying it
                self.movie.frameChanged.connect(self.onFirstFrame)
                self.movie.start()
            except Exception as e:
                print(f"Failed to load gif: {e}")

    def searchGiphyAndLoad(self):
        dialog = GiphySearchDialog(self.giphykey, self.loadGifFromUrl, self)
        accent = "#e50914"
        try:
            with open(resourcePath("config/settings.json"), "r") as f:
                accent = json.load(f).get("accent", accent)
        except:
            pass
        accentName = {
            "#e50914": "red",
            "#1e90ff": "blue",
            "#00c853": "green",
            "#9c27b0": "purple",
            "#ff69b4": "pink"
        }.get(accent, "red")
        dialog.updateLoadingSpinner(accentName)
        dialog.exec()

    def loadGifFromUrl(self, gifUrl):
        try:
            response = requests.get(gifUrl)
            if response.status_code == 200:
                tempFile = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
                tempFile.write(response.content)
                tempFile.close()
                if hasattr(self, "movie"):
                    self.movie.stop()
                    del self.movie
                self.movie = QMovie(tempFile.name)
                self.label.setMovie(self.movie)
                self.movie.frameChanged.connect(self.onFirstFrame)
                self.movie.start()
            else:
                QMessageBox.warning(self, "Error", f"Failed to load GIF (status {response.status_code})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the GIF:\n{str(e)}")

    def saveLastUsedGif(self, gifUrl):
        try:
            with open(resourcePath("../config/last_gif.json"), "w") as file:
                json.dump({"lastUsed": gifUrl}, file)
        except Exception as e:
            print(f"Failed to save last gif: {e}")

    def loadLastUsedGif(self):
        if os.path.exists(resourcePath("../config/last_gif.json")):
            try:
                with open(resourcePath("../config/last_gif.json"), "r") as file:
                    data = json.load(file)
                    lastGif = data.get("lastUsed")
                    if lastGif:
                        self.loadGifFromUrl(lastGif)
                        return True
            except json.JSONDecodeError:
                print("Failed to load last used gif: File is corrupted.")
            except Exception as e:
                print(f"Failed to load last used gif: {e}")
        return False

    def loadGifFromFile(self, filePath):
        try:
            # Check if 'movie' exists, and if so, stop it before reloading
            if hasattr(self, 'movie') and self.movie:
                self.movie.stop()
                del self.movie  # Remove the previous movie instance

            if filePath.lower().endswith(".gif"):  # Only load GIFs
                self.movie = QMovie(filePath)  # Initialize the QMovie object with the file path
                self.label.setMovie(self.movie)  # Set the movie to the label for displaying it
                self.movie.frameChanged.connect(self.onFirstFrame)  # Optional: connection for resizing
                self.movie.start()  # Start playing the movie
            else:
                pixmap = QPixmap(filePath)  # If not a GIF, load as a normal image
                if pixmap.isNull():
                    raise ValueError("Failed to load image.")
                scaled = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.label.setPixmap(scaled)
                self.label.resize(scaled.size())
                self.resize(scaled.size())
                self.aspectRatio = scaled.width() / scaled.height()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load GIF: {e}")
            self.resize(300, 300)
            self.label.resize(300, 300)  # Fallback size for failure

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange and self.isMinimized():
            QTimer.singleShot(0, self.hide)
            if not self.settings.get("suppressTrayMessage", False):
                self.tray.showMessage(
                    "GIF Widget",
                    "Widget minimized to tray. Right-click the tray icon to restore or exit.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
        super().changeEvent(event)

    def closeEvent(self, event):
        event.ignore()
        self.hide()


if __name__ == "__main__":
    import asyncio
    from qasync import QEventLoop, asyncSlot

    if trySignalExistingInstance():
        sys.exit()  # App is already running, sent "restore" command

    def listenForRestore(widget):  # ✅ this stays here
        def handle():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", PORT))
                s.listen()
                while True:
                    conn, _ = s.accept()
                    with conn:
                        data = conn.recv(1024)
                        if data == b"restore":
                            widget.showNormal()
                            widget.raise_()
                            widget.activateWindow()
        threading.Thread(target=handle, daemon=True).start()

    app = QApplication(sys.argv)

    accent = "#e50914"
    try:
        with open(resourcePath("config/settings.json"), "r") as f:
            accent = json.load(f).get("accent", accent)
    except:
        pass

    app.setStyleSheet(loadStyleWithAccent(accent))

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    widget = GifWidget(resourcePath("assets/default.png"))  # ✅ must be created before listening
    listenForRestore(widget)  # ✅ correct spot

    with loop:
        loop.run_forever()