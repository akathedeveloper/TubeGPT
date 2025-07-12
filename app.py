import streamlit as st
from utils.youtube_processor import YouTubeProcessor

st.set_page_config(page_title="TubeGPT", page_icon="🎥", layout="wide")
st.title("🎥 TubeGPT")
st.write("Enter a YouTube Video ID (11 characters) and process its transcript.")

video_id = st.text_input("YouTube Video ID", value="bMt47wvK6u0")

if st.button("Fetch Transcript"):
    yt_proc = YouTubeProcessor()
    extracted_id = yt_proc.extract_video_id(video_id)
    st.write(f"Extracted video ID: `{extracted_id}`")
    if not extracted_id:
        st.error("Invalid video ID. Please enter an 11-character ID like `bMt47wvK6u0`.")
    else:
        transcript_data, metadata = yt_proc.get_transcript_data(extracted_id)
        if not transcript_data:
            st.error(metadata.get("error", "Unknown error"))
        else:
            st.write("First 5 transcript segments (for debugging):")
            st.json(transcript_data[:5])
            transcript_text = yt_proc.process_transcript_data(transcript_data)
            st.text_area("Full Transcript", transcript_text, height=200)
            # Now chunk and show first chunk
            documents = yt_proc.process_transcript(transcript_text, extracted_id)
            if documents:
                st.write("First chunk:")
                st.write(documents[0].page_content)
            else:
                st.warning("No chunks created from transcript.")
