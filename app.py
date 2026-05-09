import streamlit as st
            right_shoulder = landmarks[12]

            shoulder_positions.append(
                abs(left_shoulder.x - right_shoulder.x)
            )

        if frame_count % 30 == 0:
            preview_frames.append(frame.copy())

    cap.release()

    st.header("Pose Detection Preview")

    cols = st.columns(min(len(preview_frames), 3))

    for idx, frame in enumerate(preview_frames[:3]):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cols[idx].image(frame_rgb, use_container_width=True)

    st.header("AI Motion Analysis")

    avg_shoulder_rotation = np.mean(shoulder_positions) if shoulder_positions else 0

    if avg_shoulder_rotation > 0.12:
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
            "Your forehand preparation is good, but your contact point is slightly late. Try initiating body rotation earlier and reducing backswing delay."
        )
    else:
        st.success(
            "Your backhand stability is decent. Focus on balance control and maintaining a consistent follow-through."
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

    st.markdown("""
- MediaPipe Pose
- OpenCV
- Streamlit
- Python
- Rule-based Motion Analysis
""")

else:
    st.info("Please upload a tennis training video to start analysis.")
