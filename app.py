import streamlit as st
import librosa
import numpy as np
import tempfile
import pandas as pd

st.set_page_config(page_title="Shot-Splits Analytics", page_icon="🔫")

st.title("🎯 Shot-Splits: Performance & Waste Analyzer")
st.write("Upload your match video to identify splits and movement waste.")

# 1. File Uploader
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Save video to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tfile:
        tfile.write(uploaded_file.read())
        
    st.video(uploaded_file)
    
    with st.spinner('Analyzing audio for shots...'):
        # 2. Extract and Load Audio
        y, sr = librosa.load(tfile.name, sr=None)
        
        # 3. Detect Onsets (Shots)
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time', backtrack=True)
        
        # 4. Create the Split Table
        if len(onsets) > 0:
            data = []
            for i in range(len(onsets)):
                cumulative = round(onsets[i], 2)
                split = round(onsets[i] - onsets[i-1], 2) if i > 0 else cumulative
                classification = "Split" if split < 2.0 else "⚠️ WASTE/TRANSITION"
                data.append([f"Shot {i+1}", cumulative, split, classification])
            
            df = pd.DataFrame(data, columns=["Event", "Cumulative Time", "Split", "Type"])
            
            st.subheader("Stage Performance Report")
            st.table(df)
            
            # 5. Lean Summary
            total_waste = df[df["Type"] == "⚠️ WASTE/TRANSITION"]["Split"].sum()
            st.metric("Total Movement/Waste Time", f"{round(total_waste, 2)}s")
        else:
            st.warning("No shots detected. Try a video with clearer audio.")
