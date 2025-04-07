# Flappy Game

A personalized Flappy Bird game with AI integration using NEAT Python.

## Features
- Customizable character using your profile picture
- AI integration using NEAT (NeuroEvolution of Augmenting Topologies)
- Customizable game settings
- Score tracking
- Modern web interface

## Requirements
- Python 3.7+
- Required packages (install using `pip install -r requirements.txt`):
  - pygame-ce
  - neat-python
  - numpy
  - Pillow

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the game:
   - Open `game_config.json`
   - Set your name in the `PLAYER_NAME` field
   - Adjust other settings as desired

3. Add your profile picture:
   - Place your profile picture in the project directory
   - Name it `profile_picture.jpg` (or update the path in `flappy_game.py`)

## How to Run

1. Run the game:
   ```bash
   python flappy_game.py
   ```

2. Controls:
   - SPACE: Make the bird flap
   - R: Restart after game over
   - A: Toggle AI control

## AI Integration

The game includes AI integration using NEAT Python. To train the AI:

1. Make sure all dependencies are installed
2. The AI can be toggled on/off during gameplay using the 'A' key
3. The AI will learn from your gameplay and improve over time

## Website

The project includes a simple website to showcase your game:
- Open `index.html` in a web browser
- Customize the content to match your game
- Add a screenshot of your game as `game_screenshot.png`

## Customization

You can customize various aspects of the game:
- Game settings in `game_config.json`
- Visual appearance in the code
- Website design in `index.html`

## Contributing

Feel free to fork this project and make your own improvements!

## License

This project is open source and available under the MIT License. 