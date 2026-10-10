
import os
import streamlit as st
from google import genai

# -------------------------------
# AI INTERVIEW COACH
# -------------------------------

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide"
)

# Read Gemini API key securely
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    API_KEY = ""

API_KEY = API_KEY or os.getenv("GEMINI_API_KEY", "")

# Page design
st.title("🎯 AI Interview Coach")
st.subheader("Practice interviews with your personal AI coach")

st.write(
    "Prepare for job interviews, practise your answers, "
    "and get AI-powered feedback to improve your performance."
)

st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Interview Settings")

    role = st.text_input(
        "Job Role",
        placeholder="e.g. Python Developer"
    )

    level = st.selectbox(
        "Experience Level",
        ["Fresher", "Beginner", "Intermediate", "Experienced"]
    )

    interview_type = st.selectbox(
        "Interview Type",
        ["Technical", "HR", "General"]
    )

    language = st.selectbox(
        "Feedback Language",
        ["English", "Simple Hinglish"]
    )

# Check API key and create client
client = None

if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception:
        st.error("Unable to initialize Gemini. Check your API setup.")

# Session state
if "questions" not in st.session_state:
    st.session_state.questions = []

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# Helper function
def ask_gemini(prompt):
    """Send a prompt to Gemini and return its response."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text or "No response received. Please try again."

# Main sections
tab1, tab2, tab3 = st.tabs(
    ["📝 Generate Questions", "💬 Practise Answers", "📊 My Results"]
)

# -------------------------------
# TAB 1: GENERATE QUESTIONS
# -------------------------------
with tab1:
    st.header("Generate Interview Questions")

    st.write(
        "Choose your job role in the sidebar, "
        "then generate questions for your practice."
    )

    if st.button("✨ Generate 5 Questions", type="primary"):
        if not role.strip():
            st.warning("Please enter a job role in the sidebar.")
        elif not client:
            st.error(
                "Gemini API key is missing. Add GEMINI_API_KEY "
                "in Streamlit Secrets and restart the app."
            )
        else:
            prompt = f"""
            Act as a professional interview coach.

            Job role: {role}
            Experience level: {level}
            Interview type: {interview_type}

            Generate exactly 5 useful interview questions.
            Number them from 1 to 5.
            Keep the questions appropriate for the experience level.
            Use clear language.
            Do not provide answers.
            """

            with st.spinner("Preparing your interview questions..."):
                try:
                    result = ask_gemini(prompt)
                    st.session_state.questions = [
                        line.strip()
                        for line in result.splitlines()
                        if line.strip()
                    ]
                    st.session_state.feedback = {}
                    st.success("Questions generated!")
                except Exception as e:
                    st.error(
                        "Could not generate questions. "
                        "Check your API key, model access, and quota."
                    )
                    st.caption(f"Technical details: {e}")

    if st.session_state.questions:
        st.subheader("Your Interview Questions")
        for question in st.session_state.questions:
            st.write(question)

# -------------------------------
# TAB 2: PRACTISE ANSWERS
# -------------------------------
with tab2:
    st.header("Practise Your Answers")

    if not role.strip():
        st.info("Enter your job role in the sidebar first.")

    elif not st.session_state.questions:
        st.info("First generate questions in the Generate Questions tab.")

    else:
        question_options = st.session_state.questions

        selected_question = st.selectbox(
            "Choose a question",
            question_options
        )

        answer = st.text_area(
            "Write your answer here",
            height=180,
            placeholder="Type your interview answer..."
        )

        if st.button("🤖 Evaluate My Answer", type="primary"):
            if not answer.strip():
                st.warning("Please write your answer first.")
            elif not client:
                st.error("Please configure your Gemini API key first.")
            else:
                prompt = f"""
                You are a helpful professional interview coach.

                Job role: {role}
                Experience level: {level}
                Interview type: {interview_type}
                Candidate's preferred feedback language: {language}

                Interview question:
                {selected_question}

                Candidate's answer:
                {answer}

                Evaluate the answer fairly and constructively.

                Return these sections:
                1. Score out of 10
                2. What was good
                3. What needs improvement
                4. A sample improved answer
                5. One practical tip for the next interview

                Be encouraging. Do not invent qualifications or
                experience for the candidate.
                """

                with st.spinner("Evaluating your answer..."):
                    try:
                        feedback = ask_gemini(prompt)
                        st.session_state.feedback[selected_question] = feedback
                        st.success("Your feedback is ready!")
                    except Exception as e:
                        st.error(
                            "Evaluation failed. Check your API key, "
                            "model access, and quota."
                        )
                        st.caption(f"Technical details: {e}")

        if selected_question in st.session_state.feedback:
            st.markdown("### 🧠 AI Feedback")
            st.markdown(
                st.session_state.feedback[selected_question]
            )

# -------------------------------
# TAB 3: RESULTS
# -------------------------------
with tab3:
    st.header("📊 Your Practice Results")

    total_questions = len(st.session_state.questions)
    completed_answers = len(st.session_state.feedback)

    col1, col2 = st.columns(2)

    col1.metric("Questions Generated", total_questions)
    col2.metric("Answers Evaluated", completed_answers)

    if st.session_state.feedback:
        st.subheader("Feedback History")

        for question, feedback in st.session_state.feedback.items():
            with st.expander(question):
                st.markdown(feedback)

        report = "\n\n".join(
            f"QUESTION: {question}\n\nFEEDBACK:\n{feedback}"
            for question, feedback in st.session_state.feedback.items()
        )

        st.download_button(
            label="📥 Download Practice Report",
            data=report,
            file_name="interview_practice_report.txt",
            mime="text/plain"
        )
    else:
        st.info(
            "Your results will appear here after you evaluate an answer."
        )

st.divider()
st.caption("AI Interview Coach | BCA Project | Powered by Google Gemini")
