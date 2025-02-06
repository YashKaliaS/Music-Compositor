# Song Generator using LangGraph

## Overview
This project is a **Song Generator** that leverages **LangGraph**, an advanced graph-based framework for language models. It generates MIDI files based on user input and converts them into WAV format for playback.
![image](https://github.com/user-attachments/assets/2fe212ef-7b0e-46b1-ae27-a5c558c6b89e)
![image](https://github.com/user-attachments/assets/52a5e73f-6c29-462a-8f6a-5bcd9756fc23)

## Features
- **Graph-Based Language Processing**: Utilizes LangGraph to structure and optimize the music generation workflow.
- **MIDI Generation**: Creates a MIDI file based on user prompts.
- **MIDI to WAV Conversion**: Converts the generated MIDI file into WAV format.
- **Interactive Audio Playback**: Allows users to listen to the generated music.

## Tech Stack
- **Python** (Backend)
- **LangGraph** (Core language model workflow)
- **music21** (MIDI generation)
- **FluidSynth** or alternatives (MIDI to WAV conversion)
- **Flask/FastAPI** (Optional, for API endpoints)

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/song-generator.git
cd song-generator

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Usage
```bash
# Run the main script
python main.py
```

## Alternative to FluidSynth
If FluidSynth is not recognized or unavailable, you can use:
- **TiMidity++**: `timidity input.mid -Ow -o output.wav`
- **fluidsynth-python bindings**
- **musescore** (for GUI-based conversion)

## Troubleshooting
- **Error: 'fluidsynth' is not recognized**
  - Ensure FluidSynth is installed and added to PATH.
  - Use an alternative MIDI-to-WAV converter.
  
- **FileNotFoundError for output.wav**
  - Check if MIDI conversion was successful.
  - Ensure the correct path to the output file is used.

## Contribution
Feel free to fork this repository and submit a pull request with improvements.

## License
MIT License

