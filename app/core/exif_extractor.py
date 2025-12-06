"""EXIF data extraction using exiftool."""

import subprocess
import json
import tempfile
import os
import sys
from typing import Dict, Optional, List, Callable
from pathlib import Path

# Windows-specific flag to hide console window
SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


class ExifExtractor:
    """Extract EXIF data from PNG files using exiftool."""
    
    BATCH_SIZE = 100  # Process files in batches
    
    def __init__(self, exiftoolPath: Optional[str] = None):
        """
        Initialize EXIF extractor.
        
        Args:
            exiftoolPath: Optional path to exiftool executable
        """
        self.exiftoolPath = exiftoolPath or self._findExiftool()
    
    def _findExiftool(self) -> str:
        """Find exiftool in PATH or local directory."""
        # Check if exiftool is in PATH
        try:
            subprocess.run(
                ["exiftool", "-ver"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                creationflags=SUBPROCESS_FLAGS
            )
            return "exiftool"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Check local exiftool directory
        localExiftool = Path(__file__).parent.parent.parent / "exiftool" / "exiftool.exe"
        if localExiftool.exists():
            return str(localExiftool)
        
        # Fallback
        return "exiftool"
    
    def _extractBatchJson(self, files: List[Path], tag: str) -> Dict[str, str]:
        """
        Extract EXIF data from a batch of files using JSON output.
        
        Args:
            files: List of file paths
            tag: EXIF tag to extract (e.g., "chara" or "Ccv3")
            
        Returns:
            Dictionary mapping file paths to base64 data
        """
        if not files:
            return {}
        
        result = {}
        
        try:
            # Write file list to a temp file (handles Unicode filenames better)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                for file in files:
                    f.write(str(file) + '\n')
                argFile = f.name
            
            try:
                # Use -json for structured output, -@ to read filenames from file
                cmd = [
                    self.exiftoolPath,
                    "-json",
                    "-" + tag,
                    "-@", argFile
                ]
                
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=300,
                    creationflags=SUBPROCESS_FLAGS
                )
                
                if process.returncode == 0 and process.stdout.strip():
                    try:
                        jsonData = json.loads(process.stdout)
                        for item in jsonData:
                            sourcePath = item.get("SourceFile", "")
                            # Try both tag name variants
                            charaData = item.get(tag.capitalize(), item.get(tag, item.get(tag.upper(), "")))
                            
                            if sourcePath and charaData:
                                # Normalize path
                                filePath = Path(sourcePath)
                                if filePath.exists():
                                    normalizedPath = str(filePath.resolve())
                                else:
                                    normalizedPath = str(filePath)
                                result[normalizedPath] = charaData
                    except json.JSONDecodeError:
                        pass
            finally:
                # Clean up temp file
                try:
                    os.unlink(argFile)
                except Exception:
                    pass
        
        except subprocess.TimeoutExpired:
            print(f"[WARNING] Batch extraction timed out for {len(files)} files")
        except Exception as e:
            print(f"[WARNING] Batch extraction error: {e}")
        
        return result
    
    def _extractSingleFile(self, filePath: Path, tag: str) -> Optional[str]:
        """
        Extract EXIF data from a single file.
        
        Args:
            filePath: Path to file
            tag: EXIF tag to extract
            
        Returns:
            Base64 data or None
        """
        try:
            cmd = [
                self.exiftoolPath,
                "-s3",
                "-" + tag,
                str(filePath)
            ]
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30,
                creationflags=SUBPROCESS_FLAGS
            )
            
            if process.returncode == 0:
                data = process.stdout.strip()
                return data if data else None
        except Exception:
            pass
        
        return None
    
    def extractFromDirectory(
        self, 
        directoryPath: str,
        progressCallback: Optional[Callable[[int, int], None]] = None,
        recursive: bool = False
    ) -> Dict[str, Optional[str]]:
        """
        Extract EXIF data from all PNG files in a directory.
        
        Args:
            directoryPath: Path to directory containing PNG files
            progressCallback: Optional callback(current, total) for progress updates
            recursive: Whether to search subdirectories
            
        Returns:
            Dictionary mapping file paths to Base64 encoded EXIF data
        """
        result = {}
        directory = Path(directoryPath)
        
        if not directory.exists() or not directory.is_dir():
            return result
        
        # Get PNG files
        if recursive:
            pngFiles = list(directory.rglob("*.png"))
        else:
            pngFiles = list(directory.glob("*.png"))
        
        if not pngFiles:
            return result
        
        totalFiles = len(pngFiles)
        processedFiles = 0
        
        # Process files in batches using JSON output
        for i in range(0, totalFiles, self.BATCH_SIZE):
            batch = pngFiles[i:i + self.BATCH_SIZE]
            
            # Try primary tag (chara)
            batchResult = self._extractBatchJson(batch, "chara")
            result.update(batchResult)
            
            # Try fallback tag (Ccv3) for files without data
            missingFiles = [f for f in batch if str(f.resolve()) not in result]
            if missingFiles:
                fallbackResult = self._extractBatchJson(missingFiles, "Ccv3")
                for path, data in fallbackResult.items():
                    if path not in result:
                        result[path] = data
            
            # For any still missing, try individual extraction
            stillMissing = [f for f in batch if str(f.resolve()) not in result]
            for f in stillMissing:
                data = self._extractSingleFile(f, "chara")
                if not data:
                    data = self._extractSingleFile(f, "Ccv3")
                if data:
                    result[str(f.resolve())] = data
            
            processedFiles += len(batch)
            if progressCallback:
                progressCallback(processedFiles, totalFiles)
        
        return result
    
    def extractFromFile(self, filePath: str) -> Optional[str]:
        """
        Extract EXIF data from a single PNG file.
        
        Args:
            filePath: Path to PNG file
            
        Returns:
            Base64 encoded EXIF data or None if not found
        """
        file = Path(filePath)
        if not file.exists() or not file.suffix.lower() == ".png":
            return None
        
        # Try primary tag
        data = self._extractSingleFile(file, "chara")
        if data:
            return data
        
        # Try fallback tag
        data = self._extractSingleFile(file, "Ccv3")
        return data
