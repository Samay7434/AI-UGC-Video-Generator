import streamlit as st
from app.services.script_generator import generate_script
from app.services.tts_engine import generate_voice
from app.services.video_editor import create_video
from app.utils.script_utils import parse_script
from app.services.pexels_service import safe_search, download_video, get_best_video_file
from app.services.scene_intelligence import generate_scene_queries


# ---------- PAGE CONFIG ----------

st.set_page_config(
    page_title="AI UGC Video Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 AI UGC Video Generator")
st.write("Generate cinematic AI marketing videos automatically")

st.divider()


# ---------- SESSION STATE ----------

if "video_history" not in st.session_state:
    st.session_state.video_history = []

if "last_payload" not in st.session_state:
    st.session_state.last_payload = None


# ---------- VIDEO GENERATION PIPELINE ----------

def generate_video_pipeline(product, tone, duration, style):

    # 1️⃣ Generate script
    script = generate_script(product, tone, duration)

    parsed = parse_script(script)

    clean_text = f"{parsed['hook']} {parsed['body']} {parsed['cta']}"

    # 2️⃣ Generate voice
    audio_file = generate_voice(clean_text)

    # 3️⃣ Scene intelligence
    queries = generate_scene_queries(parsed, product, tone)

    hook_videos = safe_search("", queries["hook"])
    body_videos = safe_search("", queries["body"])
    cta_videos = safe_search("", queries["cta"])

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

    # 4️⃣ Render video
    video_file = create_video(
        audio_path=audio_file,
        script_sections=parsed,
        scene_paths=clip_paths,
        style=style
    )

    return video_file


# ---------- INPUT SECTION ----------

product = st.text_input(
    "Product",
    placeholder="Example: Apple MacBook Air M2"
)

col1, col2 = st.columns(2)

with col1:
    tone = st.selectbox(
        "Tone",
        ["tech","coding","gym","travel","lifestyle","gaming","business","education"]
    )

with col2:
    style = st.selectbox(
        "Style",
        ["ugc","fast","cinematic","minimal"]
    )


# ---------- DURATION ----------

duration_option = st.selectbox(
    "Duration",
    ["15","30","45","60","Custom"]
)

if duration_option == "Custom":
    duration = st.number_input(
        "Enter custom duration (seconds)",
        min_value=5,
        max_value=120,
        value=30,
        step=5
    )
else:
    duration = int(duration_option)

st.write(f"Selected duration: **{duration} seconds**")

st.divider()


# ---------- GENERATE VIDEO ----------

if st.button("🚀 Generate Video"):

    payload = {
        "product": product,
        "tone": tone,
        "duration": duration,
        "style": style
    }

    st.session_state.last_payload = payload

    with st.spinner("Generating AI video... please wait ⏳"):

        video_file = generate_video_pipeline(product, tone, duration, style)

    st.success("Video Generated!")

    st.session_state.video_history.insert(0, video_file)


# ---------- REGENERATE ----------

if st.session_state.last_payload:

    if st.button("🔁 Regenerate Video"):

        payload = st.session_state.last_payload

        with st.spinner("Generating new variation..."):

            video_file = generate_video_pipeline(
                payload["product"],
                payload["tone"],
                payload["duration"],
                payload["style"]
            )

        st.session_state.video_history.insert(0, video_file)

        st.rerun()


# ---------- VIDEO HISTORY ----------

if st.session_state.video_history:

    st.divider()
    st.subheader("📜 Video History")

    for i, video in enumerate(st.session_state.video_history):

        st.markdown(f"### Video {i+1}")

        st.video(video)

        with open(video, "rb") as f:
            st.download_button(
                label="⬇ Download",
                data=f,
                file_name=f"ai_video_{i+1}.mp4",
                key=f"download_{i}"
            )

        st.divider()