# import asyncio
# from tts_engine import generate_voice
# from video_editor import create_video
# from script_utils import parse_script
# from script_generator import generate_script


# async def run():

#     product = input("Enter product: ")
#     tone = input("Enter tone: ")
#     duration = int(input("Enter duration: "))

#     script = generate_script(product, tone, duration)
#     print("Generated script:\n", script)

#     parsed = parse_script(script)

#     clean_text = f"{parsed['hook']} {parsed['body']} {parsed['cta']}"

#     audio_file = await generate_voice(clean_text)
#     print("Voice ready:", audio_file)

#     print("Creating video...")
#     video_file = create_video(
#         audio_path=audio_file,
#         script_sections=parsed
#     )

#     print("Video created:", video_file)

# asyncio.run(run())

# Apple MacBook Air M2

from fastapi import FastAPI
from app.routes import video
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.include_router(video.router)

