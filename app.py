import streamlit as st
import edge_tts
import asyncio
import os
import subprocess
import time

# --- Force Install dependencies ---
os.system('pip install edge-tts')

async def generate_reel(h_top, h_main, h_ref):
    # Unique name for every video to avoid old results
    timestamp = int(time.time())
    audio_path = f"audio_{timestamp}.mp3"
    video_name = f"reel_{timestamp}.mp4"
    video_path = os.path.abspath(video_name)

    # 1. Generate Voice
    voice = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(h_main, voice)
    await communicate.save(audio_path)

    # 2. Fix Special Characters for FFmpeg (Lambi Hadees fix)
    clean_main = h_main.replace("'", "").replace('"', '').replace(":", "").replace("\n", " ")
    
    # 3. Smart Word Wrap (Har 6 words baad line break)
    words = clean_main.split()
    wrapped_text = ""
    for i, word in enumerate(words):
        wrapped_text += word + " "
        if (i + 1) % 6 == 0:
            wrapped_text += "\n"

    # 4. FFmpeg Command (With brackets to keep it safe)
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=15',
        '-i', audio_path,
        '-vf', (
            f"drawtext=text='{h_top}':fontcolor=yellow:fontsize=50:x=(w-text_w)/2:y=300, "
            f"drawtext=text='{wrapped_text}':fontcolor=white:fontsize=45:line_spacing=20:x=(w-text_w)/2:y=(h-text_h)/2, "
            f"drawtext=text='{h_ref}':fontcolor=yellow:fontsize=35:x=(w-text_w)/2:y=h-300"
        ),
        '-c:a', 'aac', '-shortest', video_path
    ]

    subprocess.run(cmd)
    
    # Cleanup audio after use
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return video_path

# --- UI Interface ---
st.set_page_config(page_title="Hadees Reel Maker", layout="centered")
st.title("🎬 Professional Hadees Reel Maker")

hook = st.text_input("Top Hook", "The Prophet ﷺ said:")
hadees_text = st.text_area("Hadees Content", "Enter your long Hadees here...", height=150)
reference = st.text_input("Reference", "Sahih Bukhari")

if st.button("Generate Professional Reel"):
    if hadees_text:
        with st.spinner("Processing your Video... Please wait 1-2 minutes"):
            try:
                final_video = asyncio.run(generate_reel(hook, hadees_text, reference))
                
                if os.path.exists(final_video):
                    st.success("Video Generated Successfully!")
                    st.video(final_video)
                    
                    with open(final_video, "rb") as f:
                        st.download_button("📥 Download Reel", f, file_name=f"hadees_reel_{int(time.time())}.mp4")
                else:
                    st.error("Something went wrong. FFmpeg could not create the file.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter Hadees text first!")
