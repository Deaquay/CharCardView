"""Main application window."""

from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter,
    QFileDialog, QSlider, QLabel, QToolBar, QStatusBar
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QAction

from app.models.character_card import CharacterCard
from app.core.exif_extractor import ExifExtractor
from app.core.card_parser import CardParser
from app.core.settings_manager import SettingsManager
from app.gui.thumbnail_grid import ThumbnailGrid
from app.gui.data_panel import DataPanel


class ExifExtractionWorker(QObject):
    """Worker thread for EXIF extraction."""
    
    finished = Signal(dict)  # Emits {filePath: base64Data}
    error = Signal(str)  # Emits error message
    
    def __init__(self, directoryPath: str):
        """
        Initialize worker.
        
        Args:
            directoryPath: Path to directory containing PNG files
        """
        super().__init__()
        self.directoryPath = directoryPath
    
    def extract(self):
        """Perform EXIF extraction."""
        try:
            extractor = ExifExtractor()
            result = extractor.extractFromDirectory(self.directoryPath)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.settings = SettingsManager()
        self.currentDirectory: Optional[str] = None
        self.cards: list[CharacterCard] = []
        self.parser = CardParser()
        
        self._setupUi()
        self._loadSettings()
    
    def _setupUi(self):
        """Set up the UI."""
        self.setWindowTitle("Character Card Viewer")
        
        # Central widget
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Thumbnail grid (left)
        self.thumbnailGrid = ThumbnailGrid()
        self.thumbnailGrid.thumbnailClicked.connect(self._onThumbnailClicked)
        self.splitter.addWidget(self.thumbnailGrid)
        
        # Data panel (right)
        self.dataPanel = DataPanel()
        self.splitter.addWidget(self.dataPanel)
        
        # Set splitter sizes (75% / 25%)
        splitterPos = self.settings.getSplitterPosition()
        self.splitter.setSizes(splitterPos)
        self.splitter.splitterMoved.connect(self._onSplitterMoved)
        
        layout.addWidget(self.splitter)
        centralWidget.setLayout(layout)
        
        # Menu bar
        self._createMenuBar()
        
        # Toolbar
        self._createToolbar()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def _createMenuBar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        fileMenu = menubar.addMenu("File")
        
        openAction = QAction("Select Folder...", self)
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self._selectFolder)
        fileMenu.addAction(openAction)
        
        fileMenu.addSeparator()
        
        exitAction = QAction("Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        # Settings menu
        settingsMenu = menubar.addMenu("Settings")
        
        thumbnailSizeAction = QAction("Thumbnail Size...", self)
        thumbnailSizeAction.triggered.connect(self._showThumbnailSizeDialog)
        settingsMenu.addAction(thumbnailSizeAction)
    
    def _createToolbar(self):
        """Create toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Thumbnail size slider
        toolbar.addWidget(QLabel("Thumbnail Size:"))
        
        self.thumbnailSlider = QSlider(Qt.Horizontal)
        self.thumbnailSlider.setMinimum(50)
        self.thumbnailSlider.setMaximum(500)
        self.thumbnailSlider.setValue(self.settings.getThumbnailSize())
        self.thumbnailSlider.setTickPosition(QSlider.TicksBelow)
        self.thumbnailSlider.setTickInterval(50)
        self.thumbnailSlider.sliderReleased.connect(self._onThumbnailSliderReleased)
        toolbar.addWidget(self.thumbnailSlider)
        
        self.sizeLabel = QLabel(str(self.thumbnailSlider.value()))
        self.thumbnailSlider.valueChanged.connect(lambda v: self.sizeLabel.setText(str(v)))
        toolbar.addWidget(self.sizeLabel)
        
        # Initialize thumbnail grid with saved size
        self.thumbnailGrid.setThumbnailSize(self.settings.getThumbnailSize())
    
    def _loadSettings(self):
        """Load window settings."""
        width, height = self.settings.getWindowGeometry()
        self.resize(width, height)
    
    def _onSplitterMoved(self, pos: int, index: int):
        """Handle splitter movement."""
        sizes = self.splitter.sizes()
        self.settings.setSplitterPosition(sizes)
    
    def _onThumbnailSliderReleased(self):
        """Handle thumbnail slider release (only update on release for performance)."""
        value = self.thumbnailSlider.value()
        self.settings.setThumbnailSize(value)
        self.thumbnailGrid.setThumbnailSize(value)
    
    def _selectFolder(self):
        """Select folder containing character cards."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Character Cards",
            str(Path.home())
        )
        
        if directory:
            self.currentDirectory = directory
            self.statusBar.showMessage("Extracting EXIF data...")
            self._extractAndLoadCards(directory)
    
    def _extractAndLoadCards(self, directoryPath: str):
        """
        Extract EXIF data and load character cards.
        
        Args:
            directoryPath: Path to directory
        """
        # Create worker thread
        self.workerThread = QThread()
        self.worker = ExifExtractionWorker(directoryPath)
        self.worker.moveToThread(self.workerThread)
        
        self.workerThread.started.connect(self.worker.extract)
        self.worker.finished.connect(self._onExtractionFinished)
        self.worker.error.connect(self._onExtractionError)
        self.worker.finished.connect(self.workerThread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.workerThread.finished.connect(self.workerThread.deleteLater)
        
        self.workerThread.start()
    
    def _onExtractionFinished(self, exifData: dict):
        """Handle EXIF extraction completion."""
        self.cards = []
        
        for filePath, base64Data in exifData.items():
            if base64Data:
                card = self.parser.parseBase64(base64Data, filePath)
                if card:
                    self.cards.append(card)
        
        self.thumbnailGrid.setCards(self.cards)
        self.statusBar.showMessage(f"Loaded {len(self.cards)} character cards")
    
    def _onExtractionError(self, errorMsg: str):
        """Handle EXIF extraction error."""
        self.statusBar.showMessage(f"Error: {errorMsg}")
    
    def _onThumbnailClicked(self, filePath: str):
        """
        Handle thumbnail click.
        
        Args:
            filePath: Path to clicked file
        """
        # Find card for this file
        card = None
        for c in self.cards:
            if c.filePath == filePath:
                card = c
                break
        
        self.dataPanel.setCard(card)
    
    def _showThumbnailSizeDialog(self):
        """Show thumbnail size dialog (already handled by slider)."""
        self.thumbnailSlider.setFocus()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.settings.setWindowGeometry(self.width(), self.height())
        event.accept()

