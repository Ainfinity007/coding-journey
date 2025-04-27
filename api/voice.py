import speech_recognition as sr
from pydub import AudioSegment

def record_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Recording for 3 minutes...")
        audio = r.listen(source, timeout=180)
    
    # Save as WAV
    audio.export("temp.wav", format="wav")
    
    # Convert to text using local Whisper
    from whisper_cpp import Whisper
    model = Whisper('~/.cache/huggingface/whisper-small-en/ggml-small.en.bin')
    return model.transcribe("temp.wav")
