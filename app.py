import os
os.system('pip install edge-tts')
os.system('pip install streamlit')
import streamlit as st
import edge_tts
import asyncio
import os
import subprocess

st.set_page_config(page_title="Hadees Reel Maker", layout="centered")
st.title("🎥 Classic Hadees Creator")

hook = st.text_input("Top Hook", "The Prophet ﷺ said:")
hadees_text = st.text_area("Hadees Content", "Enter text...")
reference = st.text_input("Reference", "Sahih Bukhari")

async def generate_reel(h_top, h_main, h_ref):
    # 1. Generate Voice
    voice = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(h_main, voice)
    await communicate.save("audio.mp3")

    # 2. Text Wrapping for Borders
    words = h_main.split()
    wrapped_text = ""
    for i, word in enumerate(words):
        wrapped_text += word + " "
        if (i + 1) % 5 == 0: wrapped_text += "\n"

    # 3. Direct FFmpeg (No SRT needed - Stable Method)
    # Using 'drawtext' to avoid file reading errors
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=15',
        '-i', 'audio.mp3',
        '-vf', (
            f"drawbox=x=40:y=40:w=1000:h=1840:color=yellow@0.8:t=10, "
            f"drawtext=text='{h_top}':fontcolor=yellow:fontsize=50:x=(w-text_w)/2:y=200, "
            f"drawtext=text='{wrapped_text}':fontcolor=white:fontsize=45:x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=20, "
            f"drawtext=text='{h_ref}':fontcolor=yellow:fontsize=35:x=(w-text_w)/2:y=h-200"
        ),
        '-c:a', 'copy', '-shortest', 'final_reel.mp4'
    ]
    
    subprocess.run(cmd)
    return "final_reel.mp4"

if st.button("Generate Professional Reel"):
    if hadees_text:
        with st.spinner("Processing... Please wait"):
            try:
                video_path = asyncio.run(generate_reel(hook, hadees_text, reference))
                st.video(video_path)
            except Exception as e:
                st.error(f"Error: {e}")
            else:
            st.warning("Please enter Hadees text first!")
