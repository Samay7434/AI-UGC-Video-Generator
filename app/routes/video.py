from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio

from app.services.script_generator import generate_script
from app.services.tts_engine import generate_voice
from app.services.video_editor import create_video
from app.utils.script_utils import parse_script
from app.services.pexels_service import safe_search, download_video, get_best_video_file
from app.services.scene_intelligence import generate_scene_queries
from app.services.scene_filter_service import filter_best_videos

router = APIRouter()


class VideoRequest(BaseModel):
    product: str
    tone: str
    duration: int
    style: str = "ugc"


@router.post("/generate")
async def generate_video(request: VideoRequest):

    async def event_stream():

        try:

            # ---------------- SCRIPT ----------------

            yield json.dumps({"status": "Generating script..."}) + "\n"

            script = generate_script(
                request.product,
                request.tone,
                request.duration
            )

            parsed = parse_script(script)

            # Send hook to frontend
            yield json.dumps({
                "type": "hook",
                "data": parsed["hook"]
            }) + "\n"

            # ---------------- VOICE ----------------

            yield json.dumps({"status": "Generating voice..."}) + "\n"

            clean_text = f"{parsed['hook']} {parsed['body']} {parsed['cta']}"

            audio_file = await generate_voice(clean_text)

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

                # Send preview clip to frontend
                yield json.dumps({
                    "type": "scene",
                    "data": clip_path
                }) + "\n"

            # ---------------- VIDEO RENDER ----------------

            yield json.dumps({"status": "Rendering video..."}) + "\n"

            video_file = create_video(
                audio_path=audio_file,
                script_sections=parsed,
                scene_paths=clip_paths,
                style=request.style
            )

            # ---------------- COMPLETE ----------------

            yield json.dumps({
                "status": "complete",
                "video_file": video_file
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