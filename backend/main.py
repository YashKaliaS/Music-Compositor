# app.py
    # main.py
from flask import Flask, request, jsonify, send_from_directory, Response
import os
import random
import music21
import json
from typing import TypedDict, Dict
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from midi2audio import FluidSynth
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__, static_folder="midi_files")
CORS(app)  # Enable CORS for all routes

# ======== Define our state and initialize LLM =========
class MusicState(TypedDict):
    musician_input: str
    melody: str
    harmony: str
    rhythm: str
    style: str
    composition: str
    midi_file: str

llm = ChatGroq(
    temperature=0.8,
    groq_api_key=os.getenv('groq_api_key') ,# Use your key
 # Replace with your actual API key
    model_name="llama3-70b-8192"
)
# Dummy invocation (for warmup/testing)
_ = llm.invoke("What is music?")

# ======== Workflow Node Functions =========
def melody_generator(state: MusicState) -> Dict:
    prompt = ChatPromptTemplate.from_template(
        "Generate a melody based on this input: {input}. Represent it as a string of notes in music21 format"
    )
    chain = prompt | llm
    melody = chain.invoke({"input": state["musician_input"]})
    print("melody_generator output:", melody.content)
    return {"melody": melody.content}

def harmony_creator(state: MusicState) -> Dict:
    prompt = ChatPromptTemplate.from_template(
        "Create harmony for this melody: {melody}. Represent it as a string of chords in music21 format"
    )
    chain = prompt | llm
    harmony = chain.invoke({"melody": state["melody"]})
    print("harmony_creator output:", harmony.content)
    return {"harmony": harmony.content}

def rhythm_analyzer(state: MusicState) -> Dict:
    prompt = ChatPromptTemplate.from_template(
        "Analyze and suggest a rhythm for this melody and harmony: {melody},{harmony}. Represent it as a string of duration in music21 format"
    )
    chain = prompt | llm
    rhythm = chain.invoke({"melody": state["melody"], "harmony": state["harmony"]})
    print("rhythm_analyzer output:", rhythm.content)
    return {"rhythm": rhythm.content}

def style_adapter(state: MusicState) -> Dict:
    prompt = ChatPromptTemplate.from_template(
        "Adapt this composition to the {style} style: Melody: {melody}, Harmony: {harmony}, Rhythm: {rhythm}. Provide the result in music21 format"
    )
    chain = prompt | llm
    adapted = chain.invoke({
        "style": state["style"],
        "melody": state["melody"],
        "harmony": state["harmony"],
        "rhythm": state["rhythm"]
    })
    print("style_adapter output:", adapted.content)
    return {"composition": adapted.content}

def midi_converter(state: MusicState) -> Dict:
    piece = music21.stream.Score()
    # Add the LLM composition as a header comment for debugging
    composition_text = f"LLM Composition:\n{state['composition']}"
    piece.insert(0, music21.expressions.TextExpression(composition_text))
    
    # Use randomness (no fixed seed) for note/chord choices.
    scales = {
        'C major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
        'C minor': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb'],
        'C harmonic minor': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'B'],
        'C melodic minor': ['C', 'D', 'Eb', 'F', 'G', 'A', 'B']
    }
    chords = {
        'C major': ['C4', 'E4', 'G4'],
        'C minor': ['C4', 'Eb4', 'G4'],
        'C diminished': ['C4', 'Eb4', 'Gb4']
    }
    def create_melody(scale_name, duration):
        melody = music21.stream.Part()
        scale = scales[scale_name]
        for i in range(duration):
            note = music21.note.Note(random.choice(scale) + '4')
            note.quarterLength = 1
            melody.append(note)
        return melody
    def create_chord_progression(duration):
        harmony_part = music21.stream.Part()
        for i in range(duration):
            chord_name = random.choice(list(chords.keys()))
            chord_obj = music21.chord.Chord(chords[chord_name])
            chord_obj.quarterLength = 1
            harmony_part.append(chord_obj)
        return harmony_part

    user_input = state["musician_input"].lower()
    if 'minor' in user_input:
        scale_name = 'C minor'
    elif 'major' in user_input:
        scale_name = 'C major'
    else:
        scale_name = random.choice(list(scales.keys()))

    melody = create_melody(scale_name, 10)
    harmony_part = create_chord_progression(10)
    final_note = music21.note.Note(scales[scale_name][0] + '4')
    final_note.quarterLength = 1
    melody.append(final_note)
    scale_key = " ".join(scale_name.split()[:2])
    final_chord = music21.chord.Chord(chords.get(scale_key, chords['C major']))
    final_chord.quarterLength = 1
    harmony_part.append(final_chord)
    piece.append(melody)
    piece.append(harmony_part)
    piece.insert(0, music21.tempo.MetronomeMark(number=60))

    output_directory = "midi_files"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, "output.mid")
    try:
        piece.write('midi', output_file_path)
        print("MIDI file generated at:", output_file_path)
    except Exception as e:
        print("Error generating MIDI file:", e)
    return {"midi_file": output_file_path}

# --- One-shot workflow for /compose endpoint ---
workflow = StateGraph(MusicState)
workflow.add_node("melody_generator", melody_generator)
workflow.add_node("harmony_creator", harmony_creator)
workflow.add_node("rhythm_analyzer", rhythm_analyzer)
workflow.add_node("style_adapter", style_adapter)
workflow.add_node("midi_converter", midi_converter)
workflow.set_entry_point("melody_generator")
workflow.add_edge("melody_generator", "harmony_creator")
workflow.add_edge("harmony_creator", "rhythm_analyzer")
workflow.add_edge("rhythm_analyzer", "style_adapter")
workflow.add_edge("style_adapter", "midi_converter")
workflow.add_edge("midi_converter", END)
app_workflow = workflow.compile()

# --- One-shot function to generate final WAV output ---
def generate_music(musician_input: str, style: str) -> str:
    inputs = {"musician_input": musician_input, "style": style}
    try:
        result = app_workflow.invoke(inputs)
        print("Final workflow result:", result)
    except Exception as e:
        print("Error during one-shot workflow:", e)
        raise e
    midi_file = result["midi_file"]
    if os.path.exists(midi_file):
        print("MIDI file exists:", midi_file)
    else:
        print("MIDI file not found!")
    # Convert MIDI to WAV using FluidSynth
    soundfont_path = "FluidR3_GM.sf2"  # Ensure this file exists in your project folder
    if not os.path.exists(soundfont_path):
        print("Soundfont file not found at:", soundfont_path)
        raise FileNotFoundError(f"Soundfont file not found at: {soundfont_path}")
    synth = FluidSynth(soundfont_path)
    wav_output = os.path.join("midi_files", "output.wav")
    try:
        synth.midi_to_audio(midi_file, wav_output)
        print("WAV file generated at:", wav_output)
    except Exception as e:
        print("Error converting MIDI to WAV:", e)
        raise e
    return wav_output

# --- Step-by-step workflow for SSE updates ---
def run_workflow_with_updates(musician_input: str, style: str):
    state: MusicState = {"musician_input": musician_input, "style": style,
                          "melody": "", "harmony": "", "rhythm": "",
                          "composition": "", "midi_file": ""}
    
    yield {"line": "Initializing workflow..."}
    
    yield {"line": "Generating melody..."}
    update = melody_generator(state)
    state.update(update)
    yield {"line": "Melody generated."}
    
    yield {"line": "Generating harmony..."}
    update = harmony_creator(state)
    state.update(update)
    yield {"line": "Harmony generated."}
    
    yield {"line": "Analyzing rhythm..."}
    update = rhythm_analyzer(state)
    state.update(update)
    yield {"line": "Rhythm analysis complete."}
    
    yield {"line": "Adapting style..."}
    update = style_adapter(state)
    state.update(update)
    yield {"line": "Style adaptation complete."}
    
    yield {"line": "Converting to MIDI..."}
    update = midi_converter(state)
    state.update(update)
    yield {"line": "MIDI conversion complete."}
    
    yield {"line": "Finalizing output..."}
    yield {"line": "Workflow complete.", "final": state}

# --- Endpoints ---
@app.route('/compose', methods=['POST'])
def compose():
    data = request.get_json()
    musician_input = data.get("musician_input", "")
    style = data.get("style", "Romantic era")
    try:
        wav_path = generate_music(musician_input, style)
        return jsonify({"success": True, "wav_url": "http://localhost:5000/midi_files/output.wav"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/compose_steps')
def compose_steps():
    musician_input = request.args.get("musician_input", "")
    style = request.args.get("style", "Romantic era")
    
    def event_stream():
        for update in run_workflow_with_updates(musician_input, style):
            yield f"data: {json.dumps(update)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/midi_files/<path:filename>')
def serve_file(filename):
    return send_from_directory("midi_files", filename)

@app.route('/')
def index():
    return "Hello, world!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
