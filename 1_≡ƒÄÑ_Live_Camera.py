import streamlit as st

from diagnosis import run_diagnosis
from theme import apply_theme, render_header, render_footer, gauge_color

st.set_page_config(page_title="Live Camera — Agro Edge", page_icon="🎥", layout="centered")
apply_theme()
render_header("Live Camera", "videocam", "Field feed")

st.markdown("""
<div class="glass-card">
    <p class="hero-desc-text">
        This is wired to your laptop/desktop webcam for now. When the ESP32-S3 +
        OV2640 camera board is deployed in the field, swap the source below for
        its MJPEG stream URL (served over your LoRa gateway's local network or
        a small on-board web server) — the rest of this page, including the
        "Diagnose this frame" button, will work unchanged.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Try a true continuous live feed via streamlit-webrtc first (uses the
# browser's webcam directly, no page reruns needed). Falls back to a
# single-frame camera_input if the package isn't installed — see
# requirements.txt to add it.
# ---------------------------------------------------------------------------
frame_for_diagnosis = None

try:
    from streamlit_webrtc import webrtc_streamer
    import av

    st.markdown('<div class="label-mono"><span class="material-symbols-outlined">sensors</span>Live Feed</div>', unsafe_allow_html=True)

    if "last_frame" not in st.session_state:
        st.session_state.last_frame = None

    def video_frame_callback(frame):
        img = frame.to_ndarray(format="bgr24")
        st.session_state.last_frame = img
        return frame

    webrtc_streamer(
        key="agro-edge-live-camera",
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": True, "audio": False},
    )

    if st.button("📸 Capture & diagnose current frame"):
        if st.session_state.last_frame is not None:
            import cv2
            from PIL import Image
            rgb = cv2.cvtColor(st.session_state.last_frame, cv2.COLOR_BGR2RGB)
            frame_for_diagnosis = Image.fromarray(rgb)
        else:
            st.warning("No frame captured yet — give the stream a second to start.")

except ModuleNotFoundError:
    st.info("Install `streamlit-webrtc` and `av` for a true continuous live feed "
            "(see requirements.txt). Using single-shot webcam capture for now.")
    camera_file = st.camera_input("Capture a frame", label_visibility="collapsed")
    if camera_file is not None:
        from PIL import Image
        frame_for_diagnosis = Image.open(camera_file)

# ---------------------------------------------------------------------------
# Run the same AI diagnosis pipeline used on the Home page
# ---------------------------------------------------------------------------
if frame_for_diagnosis is not None:
    st.image(frame_for_diagnosis, caption="Captured frame", use_container_width=True)
    result = run_diagnosis(frame_for_diagnosis)

    if not result["is_named"]:
        st.markdown(f"""
        <div class="glass-card">
            <div class="unrecognized">Detected an unlabeled class (index {result['index']}) at {result['confidence']:.1f}% confidence.</div>
        </div>
        """, unsafe_allow_html=True)
    elif result["confidence"] < 70:
        st.markdown("""
        <div class="glass-card">
            <div class="unrecognized">
                <div class="unrecognized-label">⚠ Crop Not Recognized</div>
                Try repositioning the camera so a single leaf fills more of the frame.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        color = gauge_color(result["confidence"])
        st.markdown(f"""
        <div class="glass-card">
            <div class="label-mono"><span class="material-symbols-outlined">biotech</span>Diagnosis</div>
            <div class="result-title">{result['display_name']}</div>
            <div class="label-mono" style="justify-content:space-between; margin-bottom:0.4rem;">
                <span>Confidence</span><span class="data-viz">{result['confidence']:.1f}%</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:{result['confidence']:.1f}%; background:{color};"></div></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("For full treatment recommendations and web references, see the Home page diagnosis flow.")

render_footer()
