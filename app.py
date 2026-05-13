import streamlit as st
import edge_tts
import asyncio
import os

# Page Config
st.set_page_config(page_title="Hadees Reel Maker", layout="centered")
st.title("🎥 Classic Hadees Creator")

# Inputs
hook = st.text_input("Top Hook (e.g. SubhanAllah)", "The Prophet ﷺ said:")
hadees_text = st.text_area("Hadees Content", "Enter the full Hadees here...")
reference = st.text_input("Reference", "Sahih Bukhari")

async def generate_reel(h_top, h_main, h_ref):
    # 1. Voice Generate (Christopher)
    voice = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(h_main, voice)
    await communicate.save("audio.mp3")

    # 2. Advanced SRT (Word by Word Logic)
    words = h_main.split()
    total_words = len(words)
    duration_per_word = 0.4 # Adjust speed here
    total_duration = total_words * duration_per_word + 3 

    # Building the Subtitle with styling
    # \an5 means center, \fs is font size
    srt_content = f"1\n00:00:00,000 --> {total_duration:05.2f}\n"
    srt_content += f"{{\\an8}}{{\\fs25}}{{\\c&H00FFFF&}}{h_top}\n\n" # Yellow Top Hook
    
    current_text = ""
    for i, word in enumerate(words):
        start_time = i * duration_per_word
        current_text += word + " "
        # Add new lines every 6 words to keep it inside borders
        display_text = ""
        temp_words = current_text.split()
        for j, tw in enumerate(temp_words):
            display_text += tw + " "
            if (j + 1) % 5 == 0: display_text += "\\N"
            
        srt_content += f"{i+2}\n{start_time:05.2f} --> {total_duration:05.2f}\n"
        srt_content += f"{{\\an5}}{{\\fs22}}{display_text.strip()}\n\n"

    srt_content += f"{total_words+2}\n00:00:00,000 --> {total_duration:05.2f}\n"
    srt_content += f"{{\\an2}}{{\\fs15}}{{\\c&H00FFFF&}}{h_ref}" # Yellow Ref at bottom

    with open("subs.srt", "w", encoding="utf-8") as f:
        f.write(srt_content.replace('.', ','))

    # 3. FFmpeg Magic: Black BG + Yellow Borders + Subtitles
    # Drawbox command creates the yellow border
    cmd = (
        f'ffmpeg -f lavfi -i color=c=black:s=1080x1920:d={total_duration} '
        f'-i audio.mp3 -vf "drawbox=x=40:y=40:w=1000:h=1840:color=yellow@0.8:t=10,'
        f'subtitles=subs.srt:force_style=\'Fontname=Arial,PrimaryColour=&HFFFFFF,Outline=0,Shadow=1\'" '
        f'-c:v libx264 -preset fast -crf 23 -c:a aac -shortest final_reel.mp4 -y'
    )
    os.system(cmd)
    return "final_reel.mp4"

if st.button("Generate Professional Reel"):
    if hadees_text:
        with st.spinner("Creating your masterpiece..."):
            video_path = asyncio.run(generate_reel(hook, hadees_text, reference))
            st.video(video_path)
            with open(video_path, "rb") as file:
                st.download_button("📥 Download Final Reel", file, file_name="hadees_reel.mp4")
    else:
        st.warning("Please enter Hadees text first!")
