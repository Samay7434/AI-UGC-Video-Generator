import edge_tts

async def generate_voice(text, output="voice.mp3"):

    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-AriaNeural"
    )

    await communicate.save(output)

    return output