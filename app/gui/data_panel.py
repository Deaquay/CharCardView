"""Character data display panel."""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.models.character_card import CharacterCard
from app.gui.flow_layout import FlowLayout


class DataPanel(QWidget):
    """Panel for displaying character card data."""
    
    def __init__(self, parent=None):
        """
        Initialize data panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.currentCard: Optional[CharacterCard] = None
        self.currentGreetingIndex = 0
        
        self._setupUi()
    
    def _setupUi(self):
        """Set up the UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area for content
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout()
        self.contentLayout.setSpacing(15)
        self.contentLayout.setContentsMargins(10, 10, 10, 10)
        self.contentWidget.setLayout(self.contentLayout)
        
        self.scrollArea.setWidget(self.contentWidget)
        layout.addWidget(self.scrollArea)
        
        self.setLayout(layout)
        self._showEmptyState()
    
    def _showEmptyState(self):
        """Show empty state when no card is selected."""
        self._clearContent()
        
        label = QLabel("Select a character card to view details")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #888; font-size: 14px;")
        self.contentLayout.addWidget(label)
    
    def _clearContent(self):
        """Clear all content widgets."""
        while self.contentLayout.count():
            child = self.contentLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def setCard(self, card: Optional[CharacterCard]):
        """
        Set character card to display.
        
        Args:
            card: CharacterCard instance or None
        """
        self.currentCard = card
        self.currentGreetingIndex = 0
        self._updateContent()
    
    def _updateContent(self):
        """Update the displayed content."""
        self._clearContent()
        
        if self.currentCard is None:
            self._showEmptyState()
            return
        
        card = self.currentCard
        
        # Name (header)
        nameLabel = QLabel(card.name)
        nameFont = QFont()
        nameFont.setPointSize(18)
        nameFont.setBold(True)
        nameLabel.setFont(nameFont)
        nameLabel.setWordWrap(True)
        self.contentLayout.addWidget(nameLabel)
        
        # Tags (if any)
        if card.tags:
            self._addTagsSection(card.tags)
        
        # Description
        if card.description:
            self._addSection("Description", card.description)
        
        # Personality
        if card.personality:
            self._addSection("Personality", card.personality)
        
        # Scenario
        if card.scenario:
            self._addSection("Scenario", card.scenario)
        
        # First message with navigation
        if card.firstMes or card.alternateGreetings:
            self._addGreetingSection(card)
        
        # Add spacer
        self.contentLayout.addStretch()
    
    def _addSection(self, title: str, content: str):
        """
        Add a section with title and content.
        
        Args:
            title: Section title
            content: Section content
        """
        titleLabel = QLabel(title)
        titleFont = QFont()
        titleFont.setPointSize(12)
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        self.contentLayout.addWidget(titleLabel)
        
        contentLabel = QLabel(content)
        contentLabel.setWordWrap(True)
        contentLabel.setStyleSheet("padding: 5px;")
        self.contentLayout.addWidget(contentLabel)
    
    def _addTagsSection(self, tags: list):
        """
        Add tags section with styled tag badges.
        
        Args:
            tags: List of tag strings
        """
        # Create a container with flow layout for wrapping tags
        tagsContainer = QWidget()
        tagsLayout = FlowLayout(margin=0, hSpacing=6, vSpacing=6)
        
        for tag in tags:
            if not tag:
                continue
            tagLabel = QLabel(str(tag))
            tagLabel.setStyleSheet("""
                QLabel {
                    background-color: #3a6ea5;
                    color: white;
                    padding: 4px 10px;
                    border-radius: 12px;
                    font-size: 11px;
                }
            """)
            tagsLayout.addWidget(tagLabel)
        
        tagsContainer.setLayout(tagsLayout)
        self.contentLayout.addWidget(tagsContainer)
    
    def _addGreetingSection(self, card: CharacterCard):
        """
        Add greeting section with navigation arrows.
        
        Args:
            card: CharacterCard instance
        """
        titleLabel = QLabel("Greeting")
        titleFont = QFont()
        titleFont.setPointSize(12)
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        self.contentLayout.addWidget(titleLabel)
        
        # Navigation controls
        navLayout = QHBoxLayout()
        
        prevButton = QPushButton("←")
        prevButton.setEnabled(self.currentGreetingIndex > 0)
        prevButton.clicked.connect(lambda: self._navigateGreeting(-1))
        navLayout.addWidget(prevButton)
        
        greetingLabel = QLabel(card.getCurrentGreeting(self.currentGreetingIndex))
        greetingLabel.setWordWrap(True)
        greetingLabel.setStyleSheet("padding: 5px;")
        navLayout.addWidget(greetingLabel, 1)
        
        nextButton = QPushButton("→")
        maxIndex = card.getGreetingCount() - 1
        nextButton.setEnabled(self.currentGreetingIndex < maxIndex)
        nextButton.clicked.connect(lambda: self._navigateGreeting(1))
        navLayout.addWidget(nextButton)
        
        # Greeting counter
        if card.getGreetingCount() > 1:
            counterLabel = QLabel(f"{self.currentGreetingIndex + 1} / {card.getGreetingCount()}")
            counterLabel.setStyleSheet("color: #888; font-size: 10px;")
            navLayout.addWidget(counterLabel)
        
        navWidget = QWidget()
        navWidget.setLayout(navLayout)
        self.contentLayout.addWidget(navWidget)
    
    def _navigateGreeting(self, direction: int):
        """
        Navigate between greetings.
        
        Args:
            direction: -1 for previous, 1 for next
        """
        if self.currentCard is None:
            return
        
        newIndex = self.currentGreetingIndex + direction
        maxIndex = self.currentCard.getGreetingCount() - 1
        
        if 0 <= newIndex <= maxIndex:
            self.currentGreetingIndex = newIndex
            self._updateContent()

