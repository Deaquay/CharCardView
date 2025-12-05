# Character Card Viewer

A Python desktop application for viewing character cards stored as PNG files with embedded EXIF metadata. Character card information is typically stored as Base64-encoded JSON in PNG EXIF data, which makes it difficult to browse and view. This application provides a user-friendly interface to view thumbnails and character information.

![Preview](/images/main.png)

You can have large thumbnails:

![Preview2](/images/main2.png)

## Features

- **Thumbnail Grid View**: Browse character cards in a scrollable grid with thumbnails
- **Character Information Display**: View detailed character data including name, description, personality, scenario, and greetings
- **Resizable Interface**: Adjustable splitter between thumbnail grid and data panel (default 75/25)
- **Thumbnail Size Control**: Adjustable thumbnail size with persistent settings
- **Alternate Greetings Navigation**: Navigate through multiple greeting messages with arrow controls
- **Sorted Display**: Thumbnails automatically sorted by character name
- **Async Processing**: Non-blocking EXIF extraction for smooth UI experience

## Requirements

- Python 3.12 or later
- exiftool (will be checked/installed by install.bat)
- Windows (batch scripts provided for Windows)

## Installation

1. **Run the installation script**:
   ```batch
   install.bat
   ```

   This script will:
   - Check for exiftool in PATH
   - Check for `uv` package manager (falls back to `pip` if not available)
   - Create a virtual environment
   - Install required dependencies (PySide6, Pillow)
   - Download exiftool if missing

2. **(Optional manual installation)**:
   Manual steps:
   - Create venv
   - Install Requirements
   - Make sure exiftool.exe is in path or [download](https://github.com/Deaquay/CharCardView/releases/download/exiftool/exiftool.exe) it to exiftool/

## Usage

1. **Start the application**:
   ```batch
   start.bat
   ```
   or activate venv and run with `python main.py`

2. **Select a folder**:
   - Click `File → Select Folder...` (or press `Ctrl+O`)
   - Choose a directory containing PNG character card files

3. **Browse character cards**:
   - Click on any thumbnail to view its character information
   - Use the thumbnail size slider in the toolbar to adjust thumbnail size
   - Use arrow buttons in the greeting section to navigate through alternate greetings

4. **Adjust the interface**:
   - Drag the splitter between thumbnails and data panel to resize
   - Adjust thumbnail size using the slider in the toolbar
   - Settings are automatically saved

## Character Card Format

The application supports character cards in the `chara_card_v2` and `chara_card_v3` format with the following structure:

- **EXIF Tags**: `chara` (primary) or `Ccv3` (fallback)
- **Data Format**: Base64-encoded JSON
- **Required Fields**: name, description, personality, scenario, first_mes
- **Optional Fields**: alternate_greetings (array of strings)

## Project Structure

```
CharCardView/
├── main.py                 # Application entry point
├── pyproject.toml          # Project configuration
├── requirements.txt        # Python dependencies (for pip fallback)
├── install.bat             # Installation script
├── start.bat               # Launch script
├── app/
│   ├── gui/                # GUI components
│   │   ├── main_window.py  # Main window
│   │   ├── thumbnail_grid.py  # Thumbnail grid widget
│   │   └── data_panel.py   # Character data display
│   ├── core/               # Core business logic
│   │   ├── exif_extractor.py  # EXIF data extraction
│   │   ├── card_parser.py  # JSON parsing
│   │   └── settings_manager.py  # Settings persistence
│   ├── models/             # Data models
│   │   └── character_card.py  # Character card model
│   └── utils/              # Utilities
│       └── image_utils.py  # Thumbnail generation
├── exiftool/               # exiftool binary (optional)
└── images/
    ├── icon.ico			# Icon
    ├── icon.png			# Icon
    └── main.png			# UI
```

## Keyboard Shortcuts

- `Ctrl+O`: Select folder
- `Ctrl+Q`: Exit application

## Troubleshooting

**exiftool not found:**
- Ensure exiftool is installed and in PATH, or
- Place `exiftool.exe` in the `exiftool\` directory

**No character cards displayed:**
- Verify PNG files contain valid EXIF data with `chara` or `Ccv3` tags
- Check that files are in the selected directory

**Application won't start:**
- Ensure Python 3.12+ is installed
- Run `install.bat` to set up dependencies
- Check that virtual environment was created successfully

## License

This project is provided as-is for personal use.

## Dependencies

- **PySide6**: GUI framework
- **Pillow**: Image processing and thumbnail generation
- **exiftool**: EXIF metadata extraction (external tool)
