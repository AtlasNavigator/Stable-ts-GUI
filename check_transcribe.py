import stable_whisper
import inspect

print("Loading model...")
model = stable_whisper.load_model("tiny")
print("Model loaded.")
print("Transcribe signature:", inspect.signature(model.transcribe))
