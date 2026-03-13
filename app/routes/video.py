# from fastapi import APIRouter
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# import json
# import asyncio

# from app.services.script_generator import generate_script
# from app.services.tts_engine import generate_voice
# from app.services.video_editor import create_video
# from app.utils.script_utils import parse_script
# from app.services.pexels_service import safe_search, download_video, get_best_video_file
# from app.services.scene_intelligence import generate_scene_queries
# from app.services.scene_filter_service import filter_best_videos

# router = APIRouter()


# class VideoRequest(BaseModel):
#     product: str
#     tone: str
#     duration: int
#     style: str = "ugc"


# @router.post("/generate")
# async def generate_video(request: VideoRequest):

#     async def event_stream():

#         try:

#             # ---------------- SCRIPT ----------------

#             yield json.dumps({"status": "Generating script..."}) + "\n"

#             script = generate_script(
#                 request.product,
#                 request.tone,
#                 request.duration
#             )

#             parsed = parse_script(script)

#             # Send hook to frontend
#             yield json.dumps({
#                 "type": "hook",
#                 "data": parsed["hook"]
#             }) + "\n"

#             # ---------------- VOICE ----------------

#             yield json.dumps({"status": "Generating voice..."}) + "\n"

#             clean_text = f"{parsed['hook']} {parsed['body']} {parsed['cta']}"

#             audio_file = await generate_voice(clean_text)

#             # ---------------- SCENE SEARCH ----------------

#             yield json.dumps({"status": "Searching scenes..."}) + "\n"

#             queries = generate_scene_queries(
#                 parsed,
#                 request.product,
#                 request.tone
#             )

#             hook_videos = safe_search("", queries["hook"])
#             body_videos = safe_search("", queries["body"])
#             cta_videos = safe_search("", queries["cta"])

#             # ---------------- DOWNLOAD CLIPS ----------------

#             yield json.dumps({"status": "Downloading clips..."}) + "\n"

#             videos = [
#                 hook_videos[0],
#                 hook_videos[1] if len(hook_videos) > 1 else hook_videos[0],
#                 body_videos[0],
#                 body_videos[1] if len(body_videos) > 1 else body_videos[0],
#                 body_videos[2] if len(body_videos) > 2 else body_videos[0],
#                 cta_videos[0]
#             ]

#             clip_paths = []

#             for v in videos:

#                 video_url = get_best_video_file(v)

#                 filename = f"{abs(hash(video_url))}.mp4"

#                 clip_path = download_video(video_url, filename)

#                 clip_paths.append(clip_path)

#                 # Send preview clip to frontend
#                 yield json.dumps({
#                     "type": "scene",
#                     "data": clip_path
#                 }) + "\n"

#             # ---------------- VIDEO RENDER ----------------

#             yield json.dumps({"status": "Rendering video..."}) + "\n"

#             video_file = create_video(
#                 audio_path=audio_file,
#                 script_sections=parsed,
#                 scene_paths=clip_paths,
#                 style=request.style
#             )

#             # ---------------- COMPLETE ----------------

#             yield json.dumps({
#                 "status": "complete",
#                 "video_file": video_file
#             }) + "\n"

#         except Exception as e:

#             yield json.dumps({
#                 "status": "error",
#                 "message": str(e)
#             }) + "\n"

#     return StreamingResponse(
#         event_stream(),
#         media_type="text/plain"
#     )

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
import os

from app.services.script_generator import generate_script
from app.services.tts_engine import generate_voice
from app.services.video_editor import create_video
from app.utils.script_utils import parse_script
from app.services.pexels_service import safe_search, download_video, get_best_video_file
from app.services.scene_intelligence import generate_scene_queries

router = APIRouter()

os.makedirs("cache/audio", exist_ok=True)
os.makedirs("cache/video", exist_ok=True)
os.makedirs("cache/clips", exist_ok=True)

class VideoRequest(BaseModel):
    product: str
    tone: str
    duration: int
    style: str = "ugc"
    count: int = 1


# ---------------- PARALLEL RENDER TASK ----------------

async def render_video_task(audio_file, parsed, clip_paths, style, output):

    loop = asyncio.get_event_loop()

    video_file = await loop.run_in_executor(
        None,
        create_video,
        audio_file,
        parsed,
        clip_paths,
        style,
        output
    )

    return video_file


@router.post("/generate")
async def generate_video(request: VideoRequest):

    async def event_stream():

        try:

            render_tasks = []

            for i in range(request.count):

                yield json.dumps({
                    "status": f"Preparing video {i+1}/{request.count}"
                }) + "\n"

                # ---------------- SCRIPT ----------------

                yield json.dumps({"status": "Generating script..."}) + "\n"

                script = generate_script(
                    request.product,
                    request.tone,
                    request.duration
                )

                parsed = parse_script(script)

                yield json.dumps({
                    "type": "hook",
                    "data": parsed["hook"]
                }) + "\n"

                # ---------------- VOICE ----------------

                yield json.dumps({"status": "Generating voice..."}) + "\n"

                clean_text = f"{parsed['hook']} {parsed['body']} {parsed['cta']}"

                audio_file = await generate_voice(
                    clean_text,
                    output=f"cache/audio/voice_{i}.mp3"
                )

                # ---------------- SCENE SEARCH ----------------

                yield json.dumps({"status": "Searching scenes..."}) + "\n"

                queries = generate_scene_queries(
                    parsed,
                    request.product,
                    request.tone
                )

                hook_videos = safe_search("", queries["hook"])
                body_videos = safe_search("", queries["body"])
                cta_videos = safe_search("", queries["cta"])

                # ---------------- DOWNLOAD CLIPS ----------------

                yield json.dumps({"status": "Downloading clips..."}) + "\n"

                videos = [
                    hook_videos[0],
                    hook_videos[1] if len(hook_videos) > 1 else hook_videos[0],
                    body_videos[0],
                    body_videos[1] if len(body_videos) > 1 else body_videos[0],
                    body_videos[2] if len(body_videos) > 2 else body_videos[0],
                    cta_videos[0]
                ]

                clip_paths = []

                for v in videos:

                    video_url = get_best_video_file(v)

                    filename = f"{abs(hash(video_url))}.mp4"

                    clip_path = download_video(video_url, filename)

                    clip_paths.append(clip_path)

                    yield json.dumps({
                        "type": "scene",
                        "data": clip_path
                    }) + "\n"

                # ---------------- PARALLEL RENDER TASK ----------------

                output_video = f"cache/video/video_{i}.mp4"

                task = asyncio.create_task(
                    render_video_task(
                        audio_file,
                        parsed,
                        clip_paths,
                        request.style,
                        output_video
                    )
                )

                render_tasks.append(task)

            # ---------------- RUN ALL RENDERS IN PARALLEL ----------------

            yield json.dumps({
                "status": "Rendering videos in parallel..."
            }) + "\n"

            rendered_videos = await asyncio.gather(*render_tasks)

            for video_file in rendered_videos:

                yield json.dumps({
                    "type": "video",
                    "data": video_file
                }) + "\n"

            yield json.dumps({
                "status": "complete"
            }) + "\n"

        except Exception as e:

            yield json.dumps({
                "status": "error",
                "message": str(e)
            }) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/plain"
    )