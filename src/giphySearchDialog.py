import os
import json
import asyncio
import aiohttp
import tempfile
import mimetypes
import base64
from utils import resourcePath
from urllib.parse import urlparse
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QScrollArea, QWidget, QPushButton,
    QHBoxLayout, QLabel, QMessageBox, QTabWidget, QInputDialog
)
from PyQt6.QtGui import QMovie, QIcon  # <-- Added QIcon import
from giphy import searchGiphy


class GiphySearchDialog(QDialog):
    def __init__(self, apiKey, onSelectGifCallback, parent=None):
        super().__init__(parent)
        self.apiKey = apiKey
        self.onSelectGif = onSelectGifCallback
        self.favorites: list[tuple[str, str]] = []
        self.currentQuery = ""
        self.currentOffset = 0
        self.gifResults = []
        self.isLoading = False

        self.favoritesFile = resourcePath("config/favorites.json")
        self.loadFavoritesFromFile()

        self.setWindowTitle("Search Giphy")
        self.resize(700, 700)

        # Set window icon for the dialog
        self.setWindowIcon(QIcon(resourcePath("assets/icon.ico")))  # <-- Set icon

        mainLayout = QVBoxLayout(self)

        # Tabs Layout
        self.tabWidget = QTabWidget(self)
        self.searchTab = QWidget()
        self.favoritesTab = QWidget()

        self.tabWidget.addTab(self.searchTab, "Search")
        self.tabWidget.addTab(self.favoritesTab, "Favorites")

        self.tabWidget.currentChanged.connect(self.onTabChanged)

        mainLayout.addWidget(self.tabWidget)

        # Search Layout
        self.searchLayout = QVBoxLayout(self.searchTab)
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Search Giphy...")
        self.searchInput.setFixedHeight(40)
        self.searchInput.returnPressed.connect(self.doSearch)
        self.searchLayout.addWidget(self.searchInput)

        self.scrollArea = QScrollArea()
        self.scrollArea.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.container = QWidget()
        self.containerLayout = QVBoxLayout(self.container)
        self.scrollArea.setWidget(self.container)

        self.nextButton = QPushButton("Next 5 Results")
        self.nextButton.clicked.connect(self.loadMoreResults)
        self.searchLayout.addWidget(self.scrollArea)
        self.searchLayout.addWidget(self.nextButton)

        # Loading Overlay
        self.loadingLabel = QLabel(self)
        self.loadingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loadingLabel.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: none;")
        self.loadingLabel.setVisible(False)
        loadingMovie = QMovie(resourcePath("assets/loading_red.gif"))
        self.loadingLabel.setMovie(loadingMovie)
        loadingMovie.start()
        mainLayout.addWidget(self.loadingLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        # Bottom Banner Layout (Powered by Giphy GIF)
        self.bottomBanner = QHBoxLayout()

        # Powered by Giphy GIF
        poweredByGifLabel = QLabel(self)
        poweredByGifMovie = QMovie(resourcePath("assets/PoweredBy_200_Horizontal_Light-Backgrounds_With_Logo.gif"))
        poweredByGifLabel.setMovie(poweredByGifMovie)
        poweredByGifMovie.start()
        poweredByGifLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        poweredByGifLabel.setFixedHeight(60)

        self.bottomBanner.addWidget(poweredByGifLabel)

        # Add the banner to the main layout
        mainLayout.addLayout(self.bottomBanner)

        # Favorites Tab Layout
        self.favoritesLayout = QVBoxLayout(self.favoritesTab)
        self.favoritesContainer = QWidget()
        self.favoritesContainerLayout = QVBoxLayout(self.favoritesContainer)
        self.favoritesContainer.setLayout(self.favoritesContainerLayout)

        self.addUrlButton = QPushButton("Add GIF by URL")
        self.addUrlButton.setObjectName("addUrlButton")
        self.addUrlButton.clicked.connect(self.promptAddByUrl)
        self.favoritesLayout.addWidget(self.addUrlButton)

        self.favoritesScroll = QScrollArea()
        self.favoritesScroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.favoritesScroll.setWidgetResizable(True)
        self.favoritesScroll.setWidget(self.favoritesContainer)

        self.favoritesLayout.addWidget(self.favoritesScroll)

    def onTabChanged(self, index):
        """ Handle tab changes """
        if index == 0:  # Search Tab
            self.clearLayout(self.containerLayout)
            self.loadMoreResults()
        elif index == 1:  # Favorites Tab
            self.clearLayout(self.containerLayout)
            self.refreshFavoritesView()

    def openSearchTab(self):
        """ Switch to the Search tab """
        self.tabWidget.setCurrentIndex(0)
        self.clearLayout(self.containerLayout)
        self.loadMoreResults()

    def openFavoritesTab(self):
        """ Switch to the Favorites tab """
        self.tabWidget.setCurrentIndex(1)
        self.clearLayout(self.containerLayout)
        self.refreshFavoritesView()

    def showLoading(self):
        self.loadingLabel.setVisible(True)
        self.loadingLabel.raise_()

    def hideLoading(self):
        self.loadingLabel.setVisible(False)

    def updateLoadingSpinner(self, accentName):
        spinnerPath = resourcePath(f"assets/loading_{accentName}.gif")
        if os.path.exists(spinnerPath):
            self.loadingMovie = QMovie(spinnerPath)
            self.loadingLabel.setMovie(self.loadingMovie)
            self.loadingMovie.start()

    def promptAddByUrl(self):
        """Prompt the user to enter a URL and add the GIF from it."""
        gifUrl, ok = QInputDialog.getText(self, "Add GIF by URL", "Enter direct GIF URL:")
        if ok and gifUrl:
            # Validate and download the GIF asynchronously
            asyncio.create_task(self.downloadGifByUrl(gifUrl))

    def doSearch(self):
        self.currentQuery = self.searchInput.text().strip()
        if not self.currentQuery:
            return

        self.currentOffset = 0
        self.gifResults = []

        self.clearLayout(self.containerLayout)
        self.loadMoreResults()

    def loadMoreResults(self):
        if self.isLoading:
            return

        self.isLoading = True
        self.showLoading()

        asyncio.create_task(self.asyncLoadResults())

    async def asyncLoadResults(self):
        newGifs = searchGiphy(self.currentQuery, self.apiKey, limit=5, offset=self.currentOffset)
        self.currentOffset += len(newGifs)
        self.gifResults.extend(newGifs)

        async with aiohttp.ClientSession() as session:
            for previewUrl, gifUrl in newGifs:
                try:
                    async with session.get(previewUrl) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            tempPath = self.saveGifToTempFile(data)
                            self.addGifPreview(tempPath, gifUrl)
                except Exception as e:
                    print(f"Failed to download preview: {e}")

        self.hideLoading()
        self.isLoading = False

    async def downloadGifByUrl(self, gifUrl):
        """Download and add a GIF from any URL, supporting base64 and direct GIF links."""
        try:
            if gifUrl.startswith("data:image/gif;base64,"):
                # Handle base64 encoded GIFs
                base64_data = gifUrl.split(",", 1)[1]  # Remove the "data:image/gif;base64," part
                gif_data = base64.b64decode(base64_data)  # Decode base64 data
                tempPath = self.saveGifToTempFile(gif_data)
                self.addToFavorites(tempPath, gifUrl)
                QMessageBox.information(self, "Success", "GIF added successfully from base64!")
            else:
                # Handle regular URLs
                parsed = urlparse(gifUrl)
                if not parsed.scheme or not parsed.netloc:
                    QMessageBox.warning(self, "Invalid URL", "This doesn't look like a valid URL.")
                    return

                async with aiohttp.ClientSession() as session:
                    async with session.get(gifUrl) as response:
                        content_type = response.headers.get("Content-Type", "").lower()

                        if response.status == 200 and "gif" in content_type:
                            data = await response.read()
                            tempPath = self.saveGifToTempFile(data)
                            self.addToFavorites(tempPath, gifUrl)
                            QMessageBox.information(self, "Success", "GIF added successfully!")
                        else:
                            QMessageBox.warning(self, "Invalid Content", "The URL does not point to a valid GIF.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while downloading the GIF:\n{str(e)}")

    def addGifPreview(self, gifPath, gifUrl):
        previewMovie = QMovie(gifPath)
        previewLabel = QLabel()
        previewLabel.setMovie(previewMovie)
        previewLabel.setFixedHeight(150)
        previewLabel.setCursor(Qt.CursorShape.PointingHandCursor)
        previewMovie.start()

        favoriteButton = QPushButton("⭐")
        favoriteButton.setFixedWidth(40)
        favoriteButton.clicked.connect(lambda _, path=gifPath, url=gifUrl: self.addToFavorites(path, url))

        row = QHBoxLayout()
        row.addWidget(previewLabel)
        row.addWidget(favoriteButton)
        container = QWidget()
        container.setLayout(row)
        container.setContentsMargins(4, 8, 4, 8)  # Add padding    

        previewLabel.mousePressEvent = lambda _, url=gifUrl: self.selectGif(url)
        self.containerLayout.addWidget(container)

    def selectGif(self, gifUrl):
        """When a favorite GIF is clicked, select it."""
        self.saveLastUsedGif(gifUrl)
        self.onSelectGif(gifUrl)
        self.accept()  # Close the dialog after selection

    def saveLastUsedGif(self, gifUrl):
        try:
            with open(self.lastGifFile, "w") as file:
                json.dump({"lastUsed": gifUrl}, file)
        except Exception as e:
            print(f"Failed to save last gif: {e}")

    def addToFavorites(self, localPath, gifUrl):
        """Add the GIF to the favorites list."""
        if not any(url == gifUrl for _, url in self.favorites):
            self.favorites.append((localPath, gifUrl))
            self.saveFavoritesToFile()
            self.addFavoritePreview(localPath, gifUrl)
            QMessageBox.information(self, "Added", "GIF added to favorites!")

    def addFavoritePreview(self, gifPath, gifUrl):
        previewMovie = QMovie(gifPath)
        previewLabel = QLabel()
        previewLabel.setMovie(previewMovie)
        previewLabel.setFixedHeight(150)
        previewMovie.start()

        removeButton = QPushButton("❌")
        removeButton.setFixedWidth(40)
        removeButton.clicked.connect(lambda _, path=gifPath, url=gifUrl: self.removeFavorite(path, url))

        # Set the mouse press event to allow for GIF selection
        previewLabel.mousePressEvent = lambda event, url=gifUrl: self.selectGif(url)

        row = QHBoxLayout()
        row.addWidget(previewLabel)
        row.addWidget(removeButton)

        container = QWidget()
        container.setLayout(row)
        container.setContentsMargins(4, 8, 4, 8)  # Add padding
        self.favoritesContainerLayout.addWidget(container)

    def removeFavorite(self, gifPath, gifUrl):
        """Remove the GIF from favorites."""
        self.favorites = [(p, u) for p, u in self.favorites if u != gifUrl]
        self.saveFavoritesToFile()
        self.refreshFavoritesView()

    def clearLayout(self, layout):
        """Clear all widgets from the given layout."""
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget:
                widget.setParent(None)


    def saveGifToTempFile(self, data):
        """Save the given data to a temporary file and return its path."""
        tempFile = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
        tempFile.write(data)
        tempFile.close()
        return tempFile.name

    def refreshFavoritesView(self):
        """Refresh the favorites view to reflect any changes."""
        self.clearLayout(self.favoritesContainerLayout)
        for localPath, gifUrl in self.favorites:
            self.addFavoritePreview(localPath, gifUrl)

    def saveFavoritesToFile(self):
        """Save the favorites list to a file."""
        try:
            with open(self.favoritesFile, "w") as file:
                json.dump(self.favorites, file)
        except Exception as e:
            print(f"Failed to save favorites: {e}")

    def loadFavoritesFromFile(self):
        """Load the favorites list from a file."""
        if os.path.exists(self.favoritesFile):
            try:
                with open(self.favoritesFile, "r") as file:
                    self.favorites = json.load(file)
            except Exception as e:
                print(f"Failed to load favorites: {e}")
                self.favorites = []
        else:
            self.favorites = []
