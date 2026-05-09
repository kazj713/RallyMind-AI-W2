import streamlit as st
import cv2
import mediapipe as mp
import tempfile
import numpy as np

st.set_page_config(
    page_title="RallyMind AI",
    layout="wide"
)

st.title("🎾 RallyMind AI")
st.subheader("AI Tennis Motion Analysis Prototype")

st.markdown(
    """
### W2 Runnable Prototype

Core Features:
- Tennis Motion Recognition
- Pose Detection
- AI Motion Feedback
- Contact Timing Estimation
"""
)

uploaded_file = st.file_uploader(
    "Upload Tennis Training Video",
    type=["mp4", "mov", "avi"]
)

if uploaded_file:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    st.video(tfile.name)

    st.success("Video Uploaded Successfully")

    mp_pose = mp.solutions.pose

    pose = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(tfile.name)

    frame_count = 0
    shoulder_positions = []
    preview_frames = []

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = pose.process(rgb_frame)

        if results.pose_landmarks:

            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

            landmarks = results.pose_landmarks.landmark

            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]

            shoulder_distance = abs(
                left_shoulder.x - right_shoulder.x
            )

            shoulder_positions.append(
                shoulder_distance
            )

        if frame_count % 30 == 0:
            preview_frames.append(frame.copy())

    cap.release()

    st.header("Pose Detection Preview")

    if len(preview_frames) > 0:

        cols = st.columns(
            min(len(preview_frames), 3)
        )

        for idx, frame in enumerate(
            preview_frames[:3]
        ):

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            cols[idx].image(
                frame_rgb,
                use_container_width=True
            )

    st.header("AI Motion Analysis")

    avg_rotation = (
        np.mean(shoulder_positions)
        if shoulder_positions
        else 0
    )

    if avg_rotation > 0.12:

        motion_type = "Forehand"
        motion_score = 82
        contact_timing = "Slightly Late"

    else:

        motion_type = "Backhand"
        motion_score = 74
        contact_timing = "Stable"

    st.metric(
        "Detected Motion",
        motion_type
    )

    st.metric(
        "Motion Score",
        f"{motion_score}/100"
    )

    st.metric(
        "Contact Timing",
        contact_timing
    )

    st.header("AI Coaching Feedback")

    if motion_type == "Forehand":

        st.success(
            "Your forehand preparation is good, but your contact point is slightly late. Try rotating earlier."
        )

    else:

        st.success(
            "Your backhand stability is decent. Focus on balance and follow-through consistency."
        )

    st.header("Prototype Workflow")

    st.code(
        """
Video Upload
→ Pose Detection
→ Motion Analysis
→ Contact Timing Estimation
→ AI Feedback
→ Result Output
"""
    )

    st.header("Technical Stack")

    st.markdown(
        """
- MediaPipe Pose
- OpenCV
- Streamlit
- Python
- Rule-based Motion Analysis
"""
    )

else:

    st.info(
        "Please upload a tennis training video to start analysis."
    )    pose = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(tfile.name)

    frame_count = 0
    shoulder_positions = []
    preview_frames = []

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = pose.process(rgb_frame)

        if results.pose_landmarks:

            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

            landmarks = results.pose_landmarks.landmark

            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]

            shoulder_distance = abs(
                left_shoulder.x - right_shoulder.x
            )

            shoulder_positions.append(shoulder_distance)

        if frame_count % 30 == 0:
            preview_frames.append(frame.copy())

    cap.release()

    st.header("Pose Detection Preview")

    cols = st.columns(min(len(preview_frames), 3))

    for idx, frame in enumerate(preview_frames[:3]):

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        cols[idx].image(
            frame_rgb,
            use_container_width=True
        )

    st.header("AI Motion Analysis")

    avg_rotation = (
        np.mean(shoulder_positions)
        if shoulder_positions
        else 0
    )

    if avg_rotation > 0.12:

        motion_type = "Forehand"
        motion_score = 82
        contact_timing = "Slightly Late"

    else:

        motion_type = "Backhand"
        motion_score = 74
        contact_timing = "Stable"

    st.metric("Detected Motion", motion_type)
    st.metric("Motion Score", f"{motion_score}/100")
    st.metric("Contact Timing", contact_timing)

    st.header("AI Coaching Feedback")

    if motion_type == "Forehand":

        st.success(
            "Your forehand preparation is good, but your contact point is slightly late. Try rotating earlier."
        )

    else:

        st.success(
            "Your backhand stability is decent. Focus on balance and follow-through consistency."
        )

    st.header("Prototype Workflow")

    st.code("""
Video Upload
→ Pose Detection
→ Motion Analysis
→ Contact Timing Estimation
→ AI Feedback
→ Result Output
    """)

    st.header("Technical Stack")

    st.markdown("""
- MediaPipe Pose
- OpenCV
- Streamlit
- Python
- Rule-based Motion Analysis
""")

else:

    st.info(
        "Please upload a tennis training video to start analysis."
    )""")

else:
    st.info("Please upload a tennis training video to start analysis.")
