import streamlit as st
import os
import subprocess
import asyncio
import time

# --- AI SELF-SETUP ---
# Ye hissa khud hi software install karega
def initial_setup():
    if not os.path.exists("ffmpeg"):
        try:
            os.system('pip install edge-tts')
        except:
            pass

initial_setup()
import edge_tts

async def generate_final_video(text):
    ts = int(time.time())
    v_name = f"hadees_{ts}.mp4"
    a_name = f"voice_{ts}.mp3"
    
    # 1. Voice Generation
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(a_name)
    
    # 2. Text Formatting (Lambi Hadees fix)
    words = text.split()
    lines = [" ".join(words[i:i+5]) for i in range(0, len(words), 5)]
    wrapped = "\n".join(lines)
    wrapped = wrapped.replace("'", "").replace('"', '')

    # 3. Direct FFmpeg Engine
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=10',
        '-i', a_name,
        '-vf', f"drawtext=text='{wrapped}':fontcolor=white:fontsize=45:x=(w-text_w)/2:y=(h-text_h)/2",
        '-c:a', 'aac', '-shortest', v_name
    ]
    
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if os.path.exists(a_name):
        os.remove(a_name)
    return v_name

# --- SIMPLEST UI ---
st.set_page_config(page_title="AI Hadees Maker")
st.title("🕋 Google AI Powered Hadees Maker")
st.write("Naveed bhai, niche Hadees likhein aur button dabayein.")

user_input = st.text_area("Hadees Content", "Type here...", height=150)

if st.button("Create Professional Video"):
    if user_input:
        with st.spinner("AI is working... Please wait"):
            try:
                output_file = asyncio.run(generate_final_video(user_input))
                if os.path.exists(output_file):
                    st.video(output_file)
                    st.balloons()
                else:
                    st.error("Technical Error: FFmpeg install nahi ho saka. App ko Reboot karein.")
            except Exception as e:
                st.error(f"Error: {e}")
