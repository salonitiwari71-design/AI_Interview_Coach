import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import json


# ==========================================
# LOAD GEMINI API KEY
# ==========================================

load_dotenv()

api_key =
os.getenv("GEMINI_API_KEY")

if not api_key :
    st.error("GEMINI API Key not found. "
             "please check your .env file.")
    st.stop()


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(api_key=api_key)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="centered"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: gray;
        margin-bottom: 30px;
    }

    .question-box {
        padding: 20px;
        border-radius: 15px;
        background-color: #f1f5f9;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .score {
        font-size: 35px;
        font-weight: bold;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# SESSION STATE
# ==========================================

if "started" not in st.session_state:
    st.session_state.started = False

if "question" not in st.session_state:
    st.session_state.question = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "question_number" not in st.session_state:
    st.session_state.question_number = 1

if "scores" not in st.session_state:
    st.session_state.scores = []

if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False


# ==========================================
# GEMINI AI FUNCTION
# ==========================================

def ask_gemini(prompt):

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# GENERATE INTERVIEW QUESTION
# ==========================================

def generate_question(role, difficulty, question_number):

    prompt = f"""
You are a professional AI interview coach.

Candidate job role:
{role}

Interview difficulty:
{difficulty}

Question number:
{question_number}

Generate ONE realistic interview question.

Rules:
- Ask only one question.
- Do not provide the answer.
- Make it suitable for the selected job role.
- Keep it clear and professional.
- Avoid unnecessary repetition.

Return only the interview question.
"""

    return ask_gemini(prompt)


# ==========================================
# EVALUATE ANSWER
# ==========================================

def evaluate_answer(role, question, answer):

    prompt = f"""
You are an expert interview evaluator.

Candidate job role:
{role}

Interview question:
{question}

Candidate answer:
{answer}

Evaluate the candidate's answer.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "score": 0,
    "strengths": [
        "strength 1",
        "strength 2"
    ],
    "weaknesses": [
        "weakness 1",
        "weakness 2"
    ],
    "tips": [
        "tip 1",
        "tip 2"
    ],
    "better_answer": "A short improved example answer"
}}

Important:
- Score must be between 0 and 10.
- Be fair.
- Be constructive.
- Do not add markdown.
- Do not add ```json.
"""

    result = ask_gemini(prompt)

    # Remove markdown if Gemini accidentally adds it
    result = result.replace("```json", "")
    result = result.replace("```", "")
    result = result.strip()

    try:

        return json.loads(result)

    except:

        return {
            "score": 0,
            "strengths": [
                "The answer was received."
            ],
            "weaknesses": [
                "The AI could not properly process the response."
            ],
            "tips": [
                "Try giving a clear and structured answer."
            ],
            "better_answer": (
                "Try answering the question again "
                "with a clear explanation and example."
            )
        }


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="title">🎯 AI Interview Coach</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Practice interviews with your personal AI coach'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# START SCREEN
# ==========================================

if not st.session_state.started:

    st.header("🚀 Start Your Mock Interview")

    name = st.text_input(
        "👤 Your Name",
        placeholder="Enter your name"
    )

    role = st.selectbox(
        "💼 Select Job Role",
        [
            "Python Developer",
            "Web Developer",
            "Data Analyst",
            "Software Developer",
            "AI / ML Intern",
            "Frontend Developer",
            "Backend Developer"
        ]
    )

    difficulty = st.selectbox(
        "🎯 Interview Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    total_questions = st.slider(
        "📝 Number of Questions",
        3,
        10,
        5
    )

    if st.button(
        "🚀 Start Interview",
        use_container_width=True
    ):

        if not name.strip():

            st.warning("Please enter your name.")

        else:

            st.session_state.name = name
            st.session_state.role = role
            st.session_state.difficulty = difficulty
            st.session_state.total_questions = total_questions

            st.session_state.question_number = 1
            st.session_state.scores = []
            st.session_state.feedback = None
            st.session_state.interview_finished = False

            with st.spinner(
                "🤖 Gemini is preparing your first question..."
            ):

                st.session_state.question = generate_question(
                    role,
                    difficulty,
                    1
                )

            st.session_state.started = True

            st.rerun()


# ==========================================
# INTERVIEW SCREEN
# ==========================================

else:

    st.success(
        f"Welcome {st.session_state.name}! "
        f"Role: {st.session_state.role}"
    )

    progress = (
        st.session_state.question_number /
        st.session_state.total_questions
    )

    st.progress(progress)

    st.write(
        f"### Question "
        f"{st.session_state.question_number} "
        f"of {st.session_state.total_questions}"
    )

    st.markdown(
        f"""
        <div class="question-box">
        <h3>🤖 Gemini Interviewer</h3>
        <p>{st.session_state.question}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    answer = st.text_area(
        "✍️ Your Answer",
        height=180,
        placeholder="Type your interview answer here..."
    )

    if st.button(
        "🧠 Evaluate My Answer",
        use_container_width=True
    ):

        if not answer.strip():

            st.warning(
                "Please write your answer first."
            )

        else:

            with st.spinner(
                "🤖 Gemini is evaluating your answer..."
            ):

                feedback = evaluate_answer(
                    st.session_state.role,
                    st.session_state.question,
                    answer
                )

            st.session_state.feedback = feedback

            st.session_state.scores.append(
                feedback["score"]
            )

            st.rerun()


# ==========================================
# FEEDBACK
# ==========================================

if st.session_state.feedback:

    feedback = st.session_state.feedback

    st.divider()

    st.header("📊 AI Feedback")

    st.markdown(
        f"""
        <div class="score">
        ⭐ {feedback["score"]}/10
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("✅ What You Did Well")

    for item in feedback["strengths"]:
        st.write("• " + item)

    st.subheader("❌ What You Can Improve")

    for item in feedback["weaknesses"]:
        st.write("• " + item)

    st.subheader("💡 Improvement Tips")

    for item in feedback["tips"]:
        st.write("• " + item)

    st.subheader("🌟 Example of a Better Answer")

    st.info(feedback["better_answer"])

    st.divider()

    # ======================================
    # NEXT QUESTION
    # ======================================

    if (
        st.session_state.question_number
        < st.session_state.total_questions
    ):

        if st.button(
            "➡️ Next Question",
            use_container_width=True
        ):

            st.session_state.question_number += 1

            with st.spinner(
                "🤖 Gemini is preparing the next question..."
            ):

                st.session_state.question = (
                    generate_question(
                        st.session_state.role,
                        st.session_state.difficulty,
                        st.session_state.question_number
                    )
                )

            st.session_state.feedback = None

            st.rerun()

    else:

        st.session_state.interview_finished = True


# ==========================================
# FINAL REPORT
# ==========================================

if st.session_state.interview_finished:

    st.divider()

    st.header("🏆 Interview Completed!")

    scores = st.session_state.scores

    if scores:

        average_score = sum(scores) / len(scores)

        st.metric(
            "Overall Score",
            f"{average_score:.1f}/10"
        )

        st.subheader("📈 Question-wise Scores")

        for i, score in enumerate(scores):

            st.write(
                f"Question {i + 1}: ⭐ {score}/10"
            )

        st.subheader("🎯 Final Advice")

        if average_score >= 8:

            st.success(
                "Excellent performance! "
                "Keep practicing to maintain consistency."
            )

        elif average_score >= 6:

            st.info(
                "Good performance. "
                "Focus on improving clarity and confidence."
            )

        else:

            st.warning(
                "Keep practicing. "
                "Focus on giving structured and detailed answers."
            )

    if st.button("🔄 Start New Interview"):

        for key in list(st.session_state.keys()):

            del st.session_state[key]

        st.rerun()
