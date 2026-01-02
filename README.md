# Puzzle Prison

A 3D escape room puzzle game built with Python and OpenGL. Navigate through two challenging rooms, solve puzzles, and escape before time runs out!

## Overview

**Puzzle Prison** is an immersive first-person/third-person puzzle game where you must solve various puzzles across two rooms to escape. You have 60 seconds to complete both challenges!

### Game Features

- **Two Unique Puzzle Rooms**
  - Room 1: Fruit Collection Puzzle
  - Room 2: Color Sequence Puzzle
- **Dual Camera Modes** - Switch between first-person and third-person views
- **Time-based Challenge** - 60 seconds to complete both rooms
- **Interactive Objects** - Boxes, keys, clues, and switches
- **3D Graphics** - Rendered using OpenGL with custom lighting

## Requirements

### Dependencies

- Python 3.x
- PyOpenGL
- PyOpenGL-accelerate (optional, for better performance)
- FreeGLUT

### Installation

Install the required packages using pip:

```bash
pip install PyOpenGL PyOpenGL-accelerate
```

**Note:** You may also need to install FreeGLUT for your operating system:
- **Windows:** Download from [FreeGLUT official website](http://freeglut.sourceforge.net/)
- **Linux:** `sudo apt-get install freeglut3 freeglut3-dev`
- **macOS:** `brew install freeglut`

## How to Play

### Starting the Game

Run the game from the command line:

```bash
python "Puzzle Prison.py"
```

### Controls

| Key | Action |
|-----|--------|
| `W` | Move forward |
| `S` | Move backward |
| `A` | Strafe left |
| `D` | Strafe right |
| `Q` | Rotate camera left |
| `E` | Rotate camera right |
| `F` | Interact with objects |
| `C` | Toggle camera mode (first-person/third-person) |
| `ESC` | Quit game |

## Game Walkthrough

### Room 1: The Fruit Puzzle

**Objective:** Collect three specific fruits (Apple, Banana, and Orange) to unlock the gate.

**How to Solve:**

1. **Explore the room** - Look for boxes, keys, and clues scattered around
2. **Read clues** - Yellow spheres contain helpful hints (press `F` near them)
3. **Find keys** - Some boxes are locked and require keys (golden objects)
4. **Open boxes** - Press `F` near unlocked boxes (brown) to open them
5. **Unlock locked boxes** - Use keys to open dark red boxes
6. **Collect required fruits:**
   - 🍎 Apple (red)
   - 🍌 Banana (yellow)
   - 🍊 Orange (orange)
7. **Escape** - Once all three required fruits are collected, the gate opens

**Tips:**
- Not all fruits are required - only collect Apple, Banana, and Orange
- Grapes are a distractor fruit
- Read the riddles on boxes for hints about their contents
- Keys have clues telling you which box they unlock

### Room 2: Color Sequence Puzzle

**Objective:** Activate colored switches in the correct sequence, then activate the central buzzer.

**How to Solve:**

1. **Check the sequence** - Look at the HUD to see the target color sequence
2. **Locate switches** - Four colored switches are positioned around the room:
   - Red
   - Blue
   - Green
   - Yellow
3. **Activate in order** - Press `F` near each switch in the correct sequence
4. **Complete the pattern** - All four switches must be activated in the right order
5. **Activate buzzer** - Once the sequence is complete, go to the center and press `F` on the central buzzer
6. **Victory!** - The game completes when you activate the buzzer correctly

**Tips:**
- If you make a mistake, the sequence resets automatically
- The target sequence is displayed in the HUD
- The central buzzer glows green when the sequence is complete
- Watch your time - you need to complete both rooms within 60 seconds!

## Scoring

Your final score is based on **time remaining** when you complete both rooms. The faster you escape, the higher your score!

## Game Mechanics

### Objects in Room 1

| Object | Description | Interaction |
|--------|-------------|-------------|
| **Brown Boxes** | Unlocked containers | Press `F` to open |
| **Dark Red Boxes** | Locked containers | Require keys to open |
| **Golden Spheres** | Keys | Press `F` to collect |
| **Yellow Spheres** | Clues | Press `F` to read |
| **Colored Spheres** | Fruits | Collected automatically when box opens |

### Objects in Room 2

| Object | Description |
|--------|-------------|
| **Colored Cylinders** | Switches to activate in sequence |
| **Central Cylinder** | Final buzzer to complete the game |

### Collision Detection

- You cannot walk through walls or locked gates
- Boxes in Room 1 have collision detection
- Gates only open when puzzles are solved

## Technical Details

### Configuration Constants

```python
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ROOM_SIZE = 20.0
WALL_HEIGHT = 8.0
TIME_LIMIT = 60  # seconds
PLAYER_HEIGHT = 1.7
PLAYER_RADIUS = 0.5
MOVE_SPEED = 0.15
ROTATION_SPEED = 2.0
```

### Camera Modes

1. **First-Person** - Default view from the player's eyes
2. **Third-Person** - External view showing your character model

## Troubleshooting

### Common Issues

**Game won't start / Import errors:**
- Ensure all dependencies are installed
- Check that FreeGLUT is properly installed on your system

**Performance issues:**
- Install PyOpenGL-accelerate for hardware acceleration
- Close other applications to free up system resources

**Display issues:**
- Update your graphics drivers
- Try running in windowed mode

**Controls not responding:**
- Make sure the game window has focus
- Check that keyboard layout is set to English

## Development

### Project Structure

- **GameState class** - Manages game state and player data
- **Room 1 objects** - Fruit, Box, Key, Clue classes
- **Room 2 logic** - Color sequence puzzle mechanics
- **Rendering** - OpenGL drawing functions for all objects
- **Input handling** - Keyboard controls and interaction system

### Customization

You can modify these variables to customize the game:

- `TIME_LIMIT` - Change game duration
- `ROOM_SIZE` - Adjust room dimensions
- `COLOR_SEQUENCE` - Modify the color puzzle (automatically randomized)
- `required_fruits` - Change which fruits are needed
- Movement speeds and camera settings

## Credits

Developed as a Python OpenGL puzzle game project.

## License

This project is provided as-is for educational and entertainment purposes.

---

**Good luck escaping the Puzzle Prison!** ⏱️🔑🎮
