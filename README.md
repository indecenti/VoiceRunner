# CyberFlap - Cyberpunk Flappy Bird Clone

CyberFlap is an enhanced Python/Pygame reimplementation of Flappy Bird with cyberpunk neon aesthetics, AI assistance, voice controls, dynamic palettes, and advanced particle effects. Features shockwaves, debris trails, glitch text, multi-layer starfields, and procedural obstacle generation for endless replayability.

## Features
- **Cyberpunk Visuals**: Dynamic neon palettes, bloom/glow shaders, shockwave explosions, rotating debris with trails.
- **Gameplay Enhancements**: Level progression, combo system, fullscreen toggle, customizable speed.
- **AI Player**: Predictive obstacle avoidance (toggle with 'I').
- **Voice Controls**: Calibrate silence/shout thresholds for jump (spacebar fallback).
- **Audio Visualizer**: Real-time equalizer overlay (toggle with 'E').
- **Performance**: Smooth 60FPS, parallax starfield, optimized rendering.

## Screenshots
*(Add gameplay GIFs/screenshots here)*

## Requirements
- Python 3.8+
- Pygame 2.5+ (`pip install pygame`)
- NumPy (`pip install numpy`) for rotations/math
- Optional: `pygame-ce` for Linux tray/fullscreen



## Controls
Action	Key/Button	Description
Jump/Start	Space / A (gamepad)	Flap wings or voice shout
AI Toggle	I	Enable/disable predictive AI
Equalizer	E / Y (gamepad)	Show audio visualizer
Speed Up	+	Increase obstacle speed
Speed Down	-	Decrease obstacle speed
Fullscreen	F	Toggle fullscreen
Calibrate Voice	C	Start voice calibration
Quit	ESC	Return to menu




## Installation
```bash
git clone https://github.com/yourusername/cyberflap.git
cd cyberflap
pip install -r requirements.txt
python main.py


