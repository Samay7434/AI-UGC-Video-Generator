import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000/generate"

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

# ---------- INPUT SECTION ----------

product = st.text_input(
    "Product",
    placeholder="Example: Apple MacBook Air M2"
)

col1, col2 = st.columns(2)

with col1:
    tone = st.selectbox(
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

with col2:
    style = st.selectbox(
        "Style",
        [
            "ugc",
            "fast",
            "cinematic",
            "minimal"
        ]
    )

# ---------- DURATION ----------

duration_option = st.selectbox(
    "Duration",
    ["15", "30", "45", "60", "Custom"]
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

    status_box = st.empty()

    response = requests.post(API_URL, json=payload, stream=True)

    video_path = None

    try:

        for line in response.iter_lines():

            if line:

                data = line.decode("utf-8")
                data = json.loads(data)

                status_box.info(data["status"])

                if data["status"] == "complete":
                    video_path = data["video_file"]

                if data["status"] == "error":
                    st.error(data["message"])
                    break

    except requests.exceptions.ChunkedEncodingError:

        st.error("Connection interrupted while generating video.")

    if video_path:

        st.success("Video Generated!")

        st.session_state.video_history.insert(0, video_path)

# ---------- REGENERATE ----------

if st.session_state.last_payload:

    if st.button("🔁 Regenerate Video"):

        status_box = st.empty()

        response = requests.post(
            API_URL,
            json=st.session_state.last_payload,
            stream=True
        )

        video_path = None

        try:

            for line in response.iter_lines():

                if line:

                    data = line.decode("utf-8")
                    data = eval(data)

                    status_box.info(data["status"])

                    if data["status"] == "complete":
                        video_path = data["video_file"]

                    if data["status"] == "error":
                        st.error(data["message"])
                        break

        except requests.exceptions.ChunkedEncodingError:

            st.error("Connection interrupted during regeneration.")

        if video_path:

            st.success("New Video Generated!")

            st.session_state.video_history.insert(0, video_path)

            st.rerun()

# ---------- VIDEO HISTORY PANEL ----------

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