# Installation Guide

This guide explains how to install and run MazeRunner on a new PC.

---

## Prerequisites

### Required Software

1. **Python 3.7 or higher**
   - Download from: https://www.python.org/downloads/
   - **Important**: During installation, check "Add Python to PATH"
   - Verify installation: Open command prompt/terminal and run:
     ```bash
     python --version
     ```
     Should show: `Python 3.x.x`

2. **pip** (Python package manager)
   - Usually comes with Python
   - Verify installation:
     ```bash
     pip --version
     ```

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: ~50MB for game files
- **Display**: 1024×768 minimum resolution

---

## Installation Methods

### Method 1: Direct Copy (Recommended)

#### Step 1: Transfer Files

Copy the entire project folder to the new PC. You need these files and folders:

**Required Files:**
```
MazeRunner/
├── main.py              # Main game entry point
├── config.py            # Configuration settings
├── game_modes.py        # Game mode management
├── maze.py              # Maze generation
├── player.py            # Player and AI agent
├── pathfinding.py       # Pathfinding algorithms
├── ui.py                # User interface
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

**Optional Files (for testing/documentation):**
```
├── tests/               # Unit tests (optional)
├── test_docs/           # Documentation (optional)
└── build/               # Web build files (optional)
```

**You can skip:**
- `__pycache__/` folders (auto-generated)
- `build/` folder (only needed for web deployment)
- `.git/` folder (if using Git)

#### Step 2: Install Dependencies

1. **Open Command Prompt/Terminal:**
   - **Windows**: Press `Win + R`, type `cmd`, press Enter
   - **macOS/Linux**: Open Terminal

2. **Navigate to the project folder:**
   ```bash
   cd path/to/MazeRunner
   ```
   Example:
   ```bash
   cd C:\Users\YourName\Desktop\MazeRunner
   ```
   or on macOS/Linux:
   ```bash
   cd ~/Desktop/MazeRunner
   ```

3. **Install pygame:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install directly:
   ```bash
   pip install pygame>=2.5.0
   ```

4. **Verify installation:**
   ```bash
   python -c "import pygame; print(pygame.version.ver)"
   ```
   Should show pygame version (e.g., `2.5.0`)

#### Step 3: Run the Game

```bash
python main.py
```

The game window should open!

---

### Method 2: Using Git (If Repository Available)

If the project is in a Git repository:

1. **Install Git** (if not installed):
   - Download from: https://git-scm.com/downloads

2. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd MazeRunner
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game:**
   ```bash
   python main.py
   ```

---

### Method 3: Create a Portable Package

For easy distribution, create a portable package:

#### Step 1: Create Installation Script

**Windows (`install.bat`):**
```batch
@echo off
echo Installing MazeRunner...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Installation complete!
echo Run the game with: python main.py
pause
```

**macOS/Linux (`install.sh`):**
```bash
#!/bin/bash
echo "Installing MazeRunner..."
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
echo "Installation complete!"
echo "Run the game with: python3 main.py"
```

Make it executable (macOS/Linux):
```bash
chmod +x install.sh
```

#### Step 2: Package Files

Create a ZIP file containing:
- All Python files (`.py`)
- `requirements.txt`
- `README.md`
- `install.bat` (Windows) or `install.sh` (macOS/Linux)
- `test_docs/` folder (optional, for documentation)

#### Step 3: Distribute

Send the ZIP file to the new PC, then:
1. Extract the ZIP
2. Run `install.bat` (Windows) or `./install.sh` (macOS/Linux)
3. Run `python main.py`

---

## Troubleshooting

### Problem: "python is not recognized"

**Solution:**
- Python is not in PATH
- **Windows**: Reinstall Python and check "Add Python to PATH"
- **macOS/Linux**: Use `python3` instead of `python`

Try:
```bash
python3 main.py
```

### Problem: "pip is not recognized"

**Solution:**
- Use `python -m pip` instead:
  ```bash
  python -m pip install -r requirements.txt
  ```

### Problem: "No module named 'pygame'"

**Solution:**
- pygame not installed correctly
- Try reinstalling:
  ```bash
  pip install --upgrade pygame
  ```
- Or use:
  ```bash
  python -m pip install pygame
  ```

### Problem: "Permission denied" (macOS/Linux)

**Solution:**
- Use `pip3` with `--user` flag:
  ```bash
  pip3 install --user -r requirements.txt
  ```
- Or use `sudo` (not recommended):
  ```bash
  sudo pip3 install -r requirements.txt
  ```

### Problem: Game window doesn't open

**Solution:**
- Check Python version (need 3.7+):
  ```bash
  python --version
  ```
- Check for error messages in terminal
- Try running with verbose output:
  ```bash
  python -v main.py
  ```

### Problem: "SDL2.dll not found" (Windows)

**Solution:**
- pygame needs SDL2 libraries
- Reinstall pygame:
  ```bash
  pip uninstall pygame
  pip install pygame
  ```

### Problem: Slow performance

**Solution:**
- Close other applications
- Check if hardware acceleration is enabled
- Reduce maze size in `config.py`:
  ```python
  MAZE_WIDTH = 25  # Default: 31
  MAZE_HEIGHT = 19  # Default: 23
  ```

---

## Quick Start Checklist

- [ ] Python 3.7+ installed
- [ ] Project files copied to new PC
- [ ] Navigated to project folder in terminal
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Verified pygame: `python -c "import pygame"`
- [ ] Ran game: `python main.py`
- [ ] Game window opened successfully

---

## Running the Game

### Basic Commands

**Start the game:**
```bash
python main.py
```

**Run tests (optional):**
```bash
python tests/run_all_tests.py
```

### Controls

- **Arrow Keys** or **WASD**: Move player
- **R**: Reset game
- **G**: Generate new maze
- **ESC**: Return to main menu
- **V**: Toggle algorithm visualization
- **C**: Toggle algorithm comparison
- **H**: Toggle hints
- **1-5**: Switch game modes

See `README.md` for full controls list.

---

## Configuration

Edit `config.py` to customize:

- **Maze size**: `MAZE_WIDTH`, `MAZE_HEIGHT`
- **AI difficulty**: `AI_DIFFICULTY` ('EASY', 'MEDIUM', 'HARD')
- **Default algorithm**: `AI_ALGORITHM`
- **Initial energy**: `INITIAL_ENERGY`
- **Terrain costs**: `TERRAIN_COSTS`

---

## Uninstallation

To remove the game:

1. **Delete the project folder**
2. **Uninstall pygame** (optional):
   ```bash
   pip uninstall pygame
   ```

**Note**: Python and pip remain installed (they may be used by other programs).

---

## Platform-Specific Notes

### Windows

- Use `python` or `py` command
- If both Python 2 and 3 are installed, use `py -3`:
  ```bash
  py -3 main.py
  ```

### macOS

- Use `python3` instead of `python`
- May need to install Python from python.org (macOS comes with Python 2.7)
- Use `pip3` for package installation

### Linux

- Use `python3` command
- Install pygame system package (optional):
  ```bash
  sudo apt-get install python3-pygame  # Ubuntu/Debian
  ```
- Or use pip:
  ```bash
  pip3 install -r requirements.txt
  ```

---

## Creating an Executable (Advanced)

If you want to create a standalone executable (no Python installation needed):

### Using PyInstaller

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Create executable:**
   ```bash
   pyinstaller --onefile --windowed main.py
   ```

3. **Find executable:**
   - Windows: `dist/main.exe`
   - macOS/Linux: `dist/main`

**Note**: Executable will be large (~50-100MB) as it includes Python and pygame.

---

## Support

If you encounter issues:

1. Check this troubleshooting section
2. Verify Python and pygame versions
3. Check error messages in terminal
4. Review `README.md` for game documentation
5. Check `test_docs/explanations/` for technical details

---

## Summary

**Quick Installation:**
```bash
# 1. Copy project folder to new PC
# 2. Open terminal in project folder
# 3. Install dependencies
pip install -r requirements.txt

# 4. Run game
python main.py
```

That's it! The game should now run on the new PC.

