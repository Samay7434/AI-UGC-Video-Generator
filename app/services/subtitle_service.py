import whisper

model = whisper.load_model("base")

def get_word_timestamps(audio_path):

    result = model.transcribe(
        audio_path,
        word_timestamps=True
    )

    words = []

    for segment in result["segments"]:
        for w in segment["words"]:
            words.append({
                "word": w["word"].strip(),
                "start": w["start"],
                "end": w["end"]
            })

    return words