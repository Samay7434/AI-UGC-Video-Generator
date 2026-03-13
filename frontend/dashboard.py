# import streamlit as st
# import requests
# import json
# import os
# import shutil
# import time

# API_URL = "http://localhost:8000/generate"
# VIDEO_DIR = "videos"

# os.makedirs(VIDEO_DIR, exist_ok=True)

# st.set_page_config(
#     page_title="UGC AI Studio",
#     page_icon="🎬",
#     layout="wide"
# )

# # ---------------- SESSION STATE ----------------

# if "history" not in st.session_state:
#     st.session_state.history = []

# # ---------------- HEADER ----------------

# st.title("🎬 AI UGC Video Studio")
# st.caption("Generate AI-powered marketing videos instantly")

# # ---------------- SIDEBAR ----------------

# st.sidebar.header("⚙ Video Settings")

# product = st.sidebar.text_input(
#     "Product",
#     placeholder="ex. Travel Backpack"
# )

# tone = st.sidebar.selectbox(
#     "Tone",
#     [
#         "tech",
#         "coding",
#         "gym",
#         "travel",
#         "lifestyle",
#         "gaming",
#         "business",
#         "education"
#     ]
# )

# duration = st.sidebar.slider(
#     "Video Duration",
#     15,
#     60,
#     45
# )

# # ---------------- TEMPLATE SELECTOR ----------------

# st.sidebar.header("🎨 Template")

# template = st.sidebar.radio(
#     "Choose Template",
#     [
#         "UGC Ad",
#         "Cinematic Promo",
#         "Fast TikTok",
#         "Minimal Brand"
#     ]
# )

# style_map = {
#     "UGC Ad": "ugc",
#     "Cinematic Promo": "cinematic",
#     "Fast TikTok": "fast",
#     "Minimal Brand": "minimal"
# }

# style = style_map[template]

# # ---------------- ANALYTICS ----------------

# st.sidebar.header("📊 Usage")

# st.sidebar.metric(
#     "Videos Generated",
#     len(st.session_state.history)
# )

# st.sidebar.metric(
#     "Total Duration Generated",
#     f"{len(st.session_state.history) * duration}s"
# )

# generate = st.sidebar.button("🚀 Generate Video")

# # ---------------- LAYOUT ----------------

# main_col, library_col = st.columns([3,1])

# # ---------------- MAIN PANEL ----------------

# with main_col:

#     st.subheader("Generation Progress")

#     progress_bar = st.progress(0)
#     status_log = st.empty()

#     st.subheader("🎯 Generated Hook")
#     hook_box = st.empty()

#     st.subheader("🎥 Scene Preview")
#     scene_preview = st.container()

# # ---------------- VIDEO LIBRARY ----------------

# with library_col:

#     st.subheader("📁 Video Library")

#     if st.session_state.history:

#         for video in reversed(st.session_state.history):
#             st.video(video)

#     else:
#         st.write("No videos generated yet.")

# # ---------------- GENERATION PROCESS ----------------

# if generate:

#     if not product:
#         st.warning("Please enter a product name.")
#         st.stop()

#     payload = {
#         "product": product,
#         "tone": tone,
#         "duration": duration,
#         "style": style
#     }

#     response = requests.post(
#         API_URL,
#         json=payload,
#         stream=True
#     )

#     video_file = None

#     step_progress = {
#         "Generating script...": 20,
#         "Generating voice...": 40,
#         "Searching scenes...": 60,
#         "Downloading clips...": 80,
#         "Rendering video...": 95
#     }

#     for line in response.iter_lines():

#         if line:

#             data = json.loads(line.decode())

#             # ---------------- HANDLE HOOK + SCENE EVENTS ----------------

#             if "type" in data:

#                 if data["type"] == "hook":
#                     hook_box.success(data["data"])

#                 elif data["type"] == "scene":
#                     scene_preview.video(data["data"])

#                 continue

#             # ---------------- HANDLE STATUS EVENTS ----------------

#             status = data.get("status")

#             if status == "complete":

#                 video_file = data["video_file"]

#                 progress_bar.progress(100)

#                 status_log.success("Video generation complete!")

#                 break

#             elif status == "error":

#                 status_log.error(data["message"])

#                 break

#             else:

#                 status_log.info(status)

#                 if status in step_progress:
#                     progress_bar.progress(step_progress[status])

#     # ---------------- SHOW FINAL VIDEO ----------------

#     if video_file:

#         saved_path = f"{VIDEO_DIR}/{int(time.time())}.mp4"

#         shutil.copy(video_file, saved_path)

#         st.session_state.history.append(saved_path)

#         st.subheader("🎬 Generated Video")

#         st.video(saved_path)

#         with open(saved_path, "rb") as f:
#             st.download_button(
#                 "⬇ Download Video",
#                 f,
#                 file_name="ugc_video.mp4"
#             )

import streamlit as st
import requests
import json
import os
import shutil
import uuid

API_URL = "http://localhost:8000/generate"
VIDEO_DIR = "videos"

os.makedirs(VIDEO_DIR, exist_ok=True)

st.set_page_config(
    page_title="UGC AI Studio",
    page_icon="🎬",
    layout="wide"
)

# ---------------- SESSION STATE ----------------

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- HEADER ----------------

st.title("🎬 AI UGC Video Studio")
st.caption("Generate AI-powered marketing videos instantly")

# ---------------- SIDEBAR ----------------

st.sidebar.header("⚙ Video Settings")

product = st.sidebar.text_input(
    "Product",
    placeholder="ex. Travel Backpack"
)

tone = st.sidebar.selectbox(
    "Tone",
    [
        "tech",
        "coding",
        "gym",
        "travel",
        "lifestyle",
        "gaming",
        "business",
        "education"
    ]
)

duration = st.sidebar.slider(
    "Video Duration",
    15,
    60,
    45
)

video_count = st.sidebar.slider(
    "Number of Ads",
    1,
    5,
    1
)

st.sidebar.header("🎨 Template")

template = st.sidebar.radio(
    "Choose Template",
    [
        "UGC Ad",
        "Cinematic Promo",
        "Fast TikTok",
        "Minimal Brand"
    ]
)

style_map = {
    "UGC Ad": "ugc",
    "Cinematic Promo": "cinematic",
    "Fast TikTok": "fast",
    "Minimal Brand": "minimal"
}

style = style_map[template]

generate = st.sidebar.button("🚀 Generate Video")

# ---------------- LAYOUT ----------------

main_col, library_col = st.columns([3,1])

# ---------------- MAIN PANEL ----------------

with main_col:

    st.subheader("⚙ Generation Progress")

    progress_bar = st.progress(0)
    status_log = st.empty()

    st.subheader("🎯 Generated Hooks")
    hook_container = st.container()

    st.subheader("🎥 Scene Preview")
    scene_preview = st.container()

    st.subheader("🎬 Generated Videos")
    video_output = st.container()

# ---------------- VIDEO LIBRARY ----------------

with library_col:

    st.subheader("📁 Video Library")

    if st.session_state.history:
        for video in reversed(st.session_state.history):
            st.video(video)
    else:
        st.write("No videos generated yet.")

# ---------------- GENERATE ----------------

if generate:

    if not product:
        st.warning("Please enter a product.")
        st.stop()

    payload = {
        "product": product,
        "tone": tone,
        "duration": duration,
        "style": style,
        "count": video_count
    }

    response = requests.post(
        API_URL,
        json=payload,
        stream=True
    )

    generated_videos = []

    for line in response.iter_lines():

        if line:

            data = json.loads(line.decode())

            # ---------------- CUSTOM EVENTS ----------------

            if "type" in data:

                # HOOK
                if data["type"] == "hook":
                    hook_container.write(f"• {data['data']}")

                # SCENE PREVIEW
                elif data["type"] == "scene":
                    scene_preview.video(data["data"])

                # GENERATED VIDEO
                elif data["type"] == "video":

                    video_file = data["data"]

                    # UNIQUE filename
                    unique_id = uuid.uuid4().hex
                    saved_path = f"{VIDEO_DIR}/{unique_id}.mp4"

                    shutil.copy(video_file, saved_path)

                    generated_videos.append(saved_path)

                    variation_number = len(generated_videos)

                    video_output.subheader(f"Ad Variation {variation_number}")
                    video_output.video(saved_path)

                    # DOWNLOAD BUTTON
                    with open(saved_path, "rb") as f:
                        video_output.download_button(
                            label=f"⬇ Download Ad {variation_number}",
                            data=f,
                            file_name=f"ad_variation_{variation_number}.mp4",
                            mime="video/mp4"
                        )

                    st.session_state.history.append(saved_path)

                continue

            # ---------------- STATUS EVENTS ----------------

            status = data.get("status")

            if status == "complete":

                progress_bar.progress(100)
                status_log.success("All videos generated!")
                break

            elif status == "error":

                status_log.error(data["message"])
                break

            else:

                status_log.info(status)

                if "Preparing video" in status:
                    progress_bar.progress(10)

                elif status == "Generating script...":
                    progress_bar.progress(25)

                elif status == "Generating voice...":
                    progress_bar.progress(40)

                elif status == "Searching scenes...":
                    progress_bar.progress(55)

                elif status == "Downloading clips...":
                    progress_bar.progress(70)

                elif "Rendering" in status:
                    progress_bar.progress(90)