import os
from moviepy import (AudioFileClip, VideoFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, concatenate_videoclips)
from app.services.subtitle_service import get_word_timestamps

# Split script into subtitle lines
def split_into_lines(text, max_words=6):
    words = text.split()
    lines = []
    current = []

    for w in words:
        current.append(w)
        if len(current) >= max_words:
            lines.append(" ".join(current))
            current = []

    if current:
        lines.append(" ".join(current))

    return lines

# CREATE ONE SCENE
from moviepy.video.fx.Loop import Loop

def create_scene(video_path, duration, start_time, word_timestamps, WIDTH, HEIGHT, subtitle_size, is_hook=False):
    clip = VideoFileClip(video_path)

    # LOOP if video shorter than needed
    if clip.duration < duration:
        clip = clip.with_effects([Loop(duration=duration)])

    # Trim exactly
    clip = clip.subclipped(0, duration)

    # resize first
    clip = clip.resized(height=HEIGHT)

    # safe crop only if width is large enough
    if clip.w > WIDTH:
        clip = clip.cropped(x_center=clip.w / 2, width=WIDTH)

    clip = clip.with_position("center") 

    if is_hook:
        clip = clip.resized(lambda t: 1 + 0.08 * t)  # stronger zoom
    else:
        clip = clip.resized(lambda t: 1 + 0.02 * t)

    subtitles = []

    scene_end = start_time + duration

    for word in word_timestamps:

        if word["start"] < start_time or word["start"] > scene_end:
            continue

        txt = TextClip(
            text=word["word"],
            font_size=110 if is_hook else subtitle_size,
            color="white",
            stroke_color="black",
            stroke_width=3,
            size=(900,200),
            method="caption"
        )

        txt = (
            txt.with_start(word["start"] - start_time)
            .with_duration(word["end"] - word["start"])
            .with_position(("center", HEIGHT * 0.78))
        )

        subtitles.append(txt)

    scene = CompositeVideoClip([clip] + subtitles, size=(WIDTH, HEIGHT))
    return scene

# MAIN VIDEO CREATOR
def create_video(audio_path="voice.mp3", script_sections=None, scene_paths=None, style="ugc", output="video.mp4"):

        # ---------- STYLE CONFIG ----------
    STYLE_CONFIG = {

        "ugc": {"subtitle_size": 70, "padding": -0.25},
        "fast": {"subtitle_size": 80, "padding": -0.35},
        "cinematic": {"subtitle_size": 60, "padding": -0.15},
        "minimal": {"subtitle_size": 55, "padding": 0}

    }

    config = STYLE_CONFIG.get(style, STYLE_CONFIG["ugc"])

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    scene1_path = scene_paths[0]
    scene2_path = scene_paths[1]
    scene3_path = scene_paths[2]

    music_path = os.path.join(base_dir, "assets", "music.mp3")

    # ---------- AUDIO ----------
    voice = AudioFileClip(audio_path)
    duration = voice.duration

    word_timestamps = get_word_timestamps(audio_path)

    music = AudioFileClip(music_path).with_volume_scaled(0.04)

    # IMPORTANT: cut music to voice duration
    music = music.subclipped(0, duration)

    final_audio = CompositeAudioClip([music, voice])
    final_audio = final_audio.with_duration(duration)

    WIDTH = 1080
    HEIGHT = 1920

    # ---------- SPLIT TEXT ----------
    hook_lines = split_into_lines(script_sections["hook"])
    body_lines = split_into_lines(script_sections["body"])
    cta_lines = split_into_lines(script_sections["cta"])

    # ---------- SCENE DURATIONS ----------
    hook_duration = voice.duration * 0.15
    body_duration = voice.duration * 0.7
    cta_duration = voice.duration * 0.15

    # ---------- CREATE SCENES ----------
    # Split durations
    hook_part = hook_duration / 2
    body_part = body_duration / 3

    # HOOK clips
    scene1 = create_scene(scene_paths[0], hook_part, 0, word_timestamps, WIDTH, HEIGHT, config["subtitle_size"], is_hook=True)
    scene2 = create_scene(scene_paths[1], hook_part, hook_part, word_timestamps, WIDTH, HEIGHT, config["subtitle_size"])

    # BODY clips
    scene3 = create_scene(scene_paths[2], body_part, hook_duration, word_timestamps, WIDTH, HEIGHT, config["subtitle_size"])
    scene4 = create_scene(scene_paths[3], body_part, hook_duration + body_part, word_timestamps, WIDTH, HEIGHT, config["subtitle_size"])
    scene5 = create_scene(scene_paths[4], body_part, hook_duration + body_part*2, word_timestamps, WIDTH, HEIGHT, config["subtitle_size"])
    
    # CTA clip
    scene6 = create_scene(scene_paths[5], cta_duration, hook_duration + body_duration, word_timestamps, WIDTH, HEIGHT, config["subtitle_size"], is_hook=True)    
    
    final_video = concatenate_videoclips(
    [scene1, scene2, scene3, scene4, scene5, scene6],
    method="compose",
    padding=-0.15
    )

    final_video = final_video.with_duration(duration)
    final_video = final_video.with_audio(final_audio)

    final_video.write_videofile(
    output,
    fps=24,
    codec="libx264",
    audio_codec="libmp3lame"
    )

    print("Voice:", voice.duration)
    print("Final audio:", final_audio.duration)
    print("Video:", final_video.duration)

    return output