import stable_whisper
import inspect

print("Stable-TS version:", stable_whisper.__version__)

# Try to find the Result class
# Usually it's stable_whisper.result.WhisperResult
try:
    from stable_whisper.result import WhisperResult
    print("Found WhisperResult class")
    print("Methods:", [x for x in dir(WhisperResult) if not x.startswith("_")])
except ImportError:
    print("Could not import WhisperResult directly")
    # specific to 2.x, maybe it's just stable_whisper.WhisperResult
    try:
        print("Methods of stable_whisper.WhisperResult:", [x for x in dir(stable_whisper.WhisperResult) if not x.startswith("_")])
    except AttributeError:
        print("stable_whisper.WhisperResult not found")

