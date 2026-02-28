import streamlit as st
import PyPDF2
import docx
import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.openai_client import get_openai_client


def run_hr_ai():

    client = get_openai_client()
    
    # Add custom styling for HR page
    st.markdown("""
    <style>
        .hr-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
        }
        .stExpander {
            background-color: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin: 1rem 0;
        }
        .stFileUploader {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 1rem;
            background-color: #f8f9fa;
        }
        .stTextArea > div > div > textarea {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }
        .stTextArea > div > div > textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        .stButton > button {
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hr-header">
        <h1 style='margin: 0; color: white;'>👥 HR AI Platform</h1>
        <p style='margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);'>
            Intelligent HR Management • CV Evaluation • Policy Assistant
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------ HELPERS ------------------

    def read_pdf(file):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    def read_docx(file):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    def similarity_score(text1, text2):
        tfidf = TfidfVectorizer(stop_words="english")
        matrix = tfidf.fit_transform([text1, text2])
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(score * 100, 2)

    def ask_llm(prompt):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content

    # ------------------ SESSION STATE ------------------

    if "hr_policies" not in st.session_state:
        st.session_state.hr_policies = ""

    if "hr_tech_questions" not in st.session_state:
        st.session_state.hr_tech_questions = []

    if "hr_tech_answers" not in st.session_state:
        st.session_state.hr_tech_answers = []

    # ------------------ ROLE SELECTION ------------------

    st.sidebar.markdown("### 👤 Role Selection")
    role = st.sidebar.selectbox(
        "Choose your role",
        ["HR Manager", "Employee"],
        label_visibility="collapsed"
    )
    st.sidebar.markdown(f"**Current Role:** {role}")
    st.sidebar.markdown("---")

    # ==================================================
    # HR MANAGER VIEW
    # ==================================================

    if role == "HR Manager":

        tab1, tab2, tab3 = st.tabs([
            "📄 CV Evaluation",
            "📘 Policy Management",
            "🛠 Technical Evaluation"
        ])

        # -------------------------------
        # TAB 1: CV EVALUATION
        # -------------------------------

        with tab1:
            st.subheader("Candidate CV Evaluation")

            cv_files = st.file_uploader(
                "Upload Candidate CVs (PDF/DOCX)",
                type=["pdf", "docx"],
                accept_multiple_files=True
            )

            jd_text = st.text_area("Paste Job Description")

            if st.button("Evaluate Candidates"):

                if cv_files and jd_text.strip():

                    results = []

                    with st.spinner("Evaluating CVs..."):

                        for cv in cv_files:
                            cv_text = read_pdf(cv) if cv.name.endswith(".pdf") else read_docx(cv)
                            sim_score = similarity_score(cv_text, jd_text)

                            prompt = f"""
                            You are a hiring expert.

                            Evaluate the CV and Job Description match.
                            Provide:
                            1. Eligibility percentage
                            2. Matching skills
                            3. Missing skills
                            4. Final recommendation

                            CV:
                            {cv_text}

                            Job Description:
                            {jd_text}
                            """

                            evaluation = ask_llm(prompt)

                            results.append({
                                "name": cv.name,
                                "score": sim_score,
                                "evaluation": evaluation
                            })

                    results = sorted(results, key=lambda x: x["score"], reverse=True)

                    st.success("Evaluation Completed")

                    # Create DataFrame and Plotly chart
                    df = pd.DataFrame(results)
                    df = df.rename(columns={"name": "Candidate", "score": "Score"})
                    
                    fig = px.bar(
                        df.sort_values("Score", ascending=False),
                        x="Score",
                        y="Candidate",
                        orientation="h",
                        color="Score",
                        color_continuous_scale="Blues"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

                    for i, r in enumerate(results, 1):
                        with st.expander(f"Rank {i}: {r['name']} ({r['score']}%)"):
                            st.write(r["evaluation"])

                else:
                    st.warning("Upload CV(s) and paste Job Description.")

        # -------------------------------
        # TAB 2: POLICY MANAGEMENT
        # -------------------------------

        with tab2:
            st.subheader("Upload HR Policy PDFs")

            policy_files = st.file_uploader(
                "Upload policy PDFs",
                type=["pdf"],
                accept_multiple_files=True
            )

            if policy_files:
                combined_text = ""

                for pdf in policy_files:
                    combined_text += f"\n--- {pdf.name} ---\n"
                    combined_text += read_pdf(pdf)

                st.session_state.hr_policies = combined_text
                st.success(f"{len(policy_files)} policy document(s) loaded successfully")

        # -------------------------------
        # TAB 3: TECHNICAL EVALUATION
        # -------------------------------

        with tab3:
            st.subheader("Technical Assessment for Candidate")

            candidate_cv = st.file_uploader(
                "Upload Candidate CV",
                type=["pdf", "docx"],
                key="tech_cv"
            )

            tech_jd_text = st.text_area("Paste Job Description", key="tech_jd")

            if st.button("Generate Technical Questions"):

                if candidate_cv and tech_jd_text.strip():

                    cv_text = read_pdf(candidate_cv) if candidate_cv.name.endswith(".pdf") else read_docx(candidate_cv)

                    prompt = f"""
                    You are a technical interviewer.

                    Based on the candidate CV and Job Description,
                    generate 5 technical interview questions.
                    Questions should increase in difficulty.
                    Number them clearly from 1 to 5.

                    Candidate CV:
                    {cv_text}

                    Job Description:
                    {tech_jd_text}
                    """

                    with st.spinner("Generating questions..."):
                        questions_text = ask_llm(prompt)

                    questions_list = [
                        q.strip() for q in questions_text.split("\n")
                        if q.strip()
                    ]

                    st.session_state.hr_tech_questions = questions_list
                    st.session_state.hr_tech_answers = [""] * len(questions_list)

                    st.success("Questions generated! Please answer below.")

            # Display questions + collect answers

            if st.session_state.hr_tech_questions:

                answers = []

                for idx, q in enumerate(st.session_state.hr_tech_questions):
                    st.write(f"**Q{idx+1}: {q}**")
                    ans = st.text_area(f"Answer for Q{idx+1}", key=f"hr_ans_{idx}")
                    answers.append(ans)

                if st.button("Submit Answers"):

                    with st.spinner("Evaluating answers..."):

                        detailed_feedback = ""
                        total_score = 0

                        for i, (q, a) in enumerate(zip(st.session_state.hr_tech_questions, answers), 1):

                            eval_prompt = f"""
                            Evaluate the candidate's answer.
                            Provide:
                            - Score (0-20)
                            - Short feedback

                            Question:
                            {q}

                            Candidate Answer:
                            {a}
                            """

                            result = ask_llm(eval_prompt)
                            detailed_feedback += f"**Q{i} Evaluation:**\n{result}\n\n"

                        st.success("Technical Evaluation Completed")
                        st.write(detailed_feedback)

    # ==================================================
    # EMPLOYEE VIEW
    # ==================================================

    else:

        st.subheader("Ask HR Policies")

        if not st.session_state.hr_policies:
            st.warning("HR policy documents not available. Contact HR.")
        else:
            question = st.text_input("Enter your policy question")

            if st.button("Ask"):

                if question.strip() == "":
                    st.warning("Enter a question")
                else:
                    prompt = f"""
                    Answer ONLY using the HR policies below.
                    If information not present, say:
                    "Policy does not specify this."

                    POLICIES:
                    {st.session_state.hr_policies}

                    QUESTION:
                    {question}
                    """

                    with st.spinner("Searching policies..."):
                        answer = ask_llm(prompt)

                    st.info("Answer")
                    st.write(answer)