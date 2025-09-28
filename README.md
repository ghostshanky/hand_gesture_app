# Hand Gesture Monitor

A real-time hand gesture recognition desktop application that monitors hand movements using computer vision and triggers system shutdown on detecting a specific gesture (middle finger extended). Built with Python, OpenCV, MediaPipe, and CustomTkinter for a modern GUI.

## Features

- **Real-Time Hand Tracking**: Uses MediaPipe for accurate hand landmark detection
- **Live Camera Feed**: Displays the camera input with overlaid hand landmarks
- **Virtual Hand Model**: 2D holographic wireframe representation of detected hand
- **Modern GUI**: Dark theme interface with status indicators and event logging
- **Full-Screen Mode**: Runs in full-screen by default with F11 toggle
- **Standalone Executable**: Packaged as a Windows executable with custom icon
- **Safety Features**: Includes safety notes and status monitoring

## Requirements

- Python 3.8+
- Webcam
- Windows (for executable), cross-platform for source code

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/ghostshanky/hand_gesture_app.git
   cd hand_gesture_app
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install opencv-python mediapipe customtkinter pillow
   ```

4. Run the application:
   ```bash
   python main.py
   ```

### Standalone Executable

Download the latest release from the [Releases](https://github.com/ghostshanky/hand_gesture_app/releases) page and run `Hand Gesture Monitor.exe`.

## Usage

1. Launch the application
2. Allow camera access when prompted
3. The app will start monitoring in real-time
4. Extend only your middle finger to trigger immediate system shutdown
5. Use F11 to toggle full-screen mode
6. Press Escape to exit full-screen



## Building from Source

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Generate the icon (optional):
   ```bash
   python create_icon.py
   ```

3. Build the executable:
   ```bash
   pyinstaller main.spec
   ```

The executable will be created in the `dist/` folder.

## Project Structure

- `main.py` - Main application code
- `create_icon.py` - Script to generate custom icon
- `main.spec` - PyInstaller specification file
- `icon.ico` - Application icon
- `TODO.md` - Development notes and completed tasks
- `.gitignore` - Git ignore file

## Dependencies

- OpenCV - Computer vision library
- MediaPipe - Hand tracking and landmark detection
- CustomTkinter - Modern GUI framework
- Pillow - Image processing
- PyInstaller - Packaging tool

## License

This project is for educational and demonstration purposes. Use at your own risk.

## Contributing

Feel free to submit issues and pull requests.

## Author

Developed as a demonstration of computer vision and gesture recognition.
