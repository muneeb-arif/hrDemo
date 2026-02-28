import streamlit as st
import PyPDF2
import docx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
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

    def extract_skills_from_jd(jd_text):
        """Extract key skill categories from Job Description"""
        prompt = f"""
        Analyze the following Job Description and extract the main skill categories/domains required.
        Return ONLY a JSON array of skill category names (3-8 skills), nothing else.
        Examples: Frontend, Backend, APIs, Testing, DevOps, Leadership, Database, Cloud, etc.
        Use concise, single-word or two-word skill names.
        
        Job Description:
        {jd_text}
        
        Return format: ["Skill1", "Skill2", "Skill3", ...]
        """
        response = ask_llm(prompt)
        try:
            # Try to extract JSON array from response
            response = response.strip()
            if response.startswith("```"):
                # Remove code block markers
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            if response.startswith("["):
                skills = json.loads(response)
                return [s.strip() for s in skills if s.strip()]
        except:
            pass
        # Fallback: return default skills if extraction fails
        return [
            "Technical / Functional Expertise",
            "Problem Solving & Analytical Thinking",
            "Communication Skills",
            "Collaboration & Teamwork",
            "Execution & Delivery",
            "Leadership & Ownership",
            "Adaptability & Learning Agility",
            "Cultural & Organizational Fit"
        ]

    def get_skill_scores(cv_text, jd_text, skills):
        """Get skill scores (0-100) for a candidate based on CV and JD"""
        prompt = f"""
        Evaluate the candidate's CV against the Job Description for each skill category.
        Return ONLY a JSON object with skill names as keys and scores (0-100) as values.
        
        Skills to evaluate: {', '.join(skills)}
        
        CV:
        {cv_text[:2000]}
        
        Job Description:
        {jd_text[:2000]}
        
        Return format: {{"Skill1": 85, "Skill2": 70, "Skill3": 80, ...}}
        """
        response = ask_llm(prompt)
        try:
            # Try to extract JSON object from response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            if response.startswith("{"):
                scores = json.loads(response)
                # Ensure all skills have scores, default to 0 if missing
                return {skill: scores.get(skill, 0) for skill in skills}
        except:
            pass
        # Fallback: return equal scores if extraction fails
        return {skill: 50 for skill in skills}

    def extract_skill_status(cv_text, jd_text):
        """Extract missing skills, absent skills, and strong skills from CV vs JD"""
        prompt = f"""
        Analyze the candidate's CV against the Job Description.
        Return ONLY a JSON object with three arrays:
        - "missing": skills mentioned in JD but weak/limited in CV (use 🟡)
        - "absent": skills required in JD but completely missing from CV (use 🔴)
        - "strong": skills that are strong/prominent in CV (use 🟢)
        
        Return only specific technology/tool names (e.g., "TypeScript", "Vue.js", "React", "Docker", etc.)
        Keep skill names concise (1-3 words max).
        
        CV:
        {cv_text[:2000]}
        
        Job Description:
        {jd_text[:2000]}
        
        Return format: {{"missing": ["Skill1", "Skill2"], "absent": ["Skill3"], "strong": ["Skill4", "Skill5"]}}
        """
        response = ask_llm(prompt)
        try:
            # Try to extract JSON object from response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            if response.startswith("{"):
                status = json.loads(response)
                return {
                    "missing": status.get("missing", []),
                    "absent": status.get("absent", []),
                    "strong": status.get("strong", [])
                }
        except:
            pass
        # Fallback: return empty lists
        return {"missing": [], "absent": [], "strong": []}

    def get_hire_recommendation(score, missing_skills, absent_skills, all_scores=None):
        """Determine hire recommendation based on score, missing skills, and relative ranking"""
        # If we have all scores, use relative ranking
        if all_scores and len(all_scores) > 1:
            avg_score = sum(all_scores) / len(all_scores)
            max_score = max(all_scores)
            
            # Relative to average and max
            if score >= max_score * 0.9:  # Top 10% of candidates
                recommendation = "Strong Hire"
                emoji = "🟢"
                color = "#16a34a"
            elif score >= avg_score * 1.2 or score >= 60:  # Above average by 20% or absolute 60%+
                recommendation = "Consider"
                emoji = "🟡"
                color = "#eab308"
            elif score >= avg_score:  # At or above average
                recommendation = "Consider"
                emoji = "🟡"
                color = "#eab308"
            else:
                recommendation = "Not Recommended"
                emoji = "🔴"
                color = "#dc2626"
        else:
            # Fallback to absolute thresholds if no comparison data
            if score >= 80:
                recommendation = "Strong Hire"
                emoji = "🟢"
                color = "#16a34a"
            elif score >= 60:
                recommendation = "Consider"
                emoji = "🟡"
                color = "#eab308"
            else:
                recommendation = "Not Recommended"
                emoji = "🔴"
                color = "#dc2626"
        
        # Calculate risk level based on missing/absent skills
        total_risks = len(missing_skills) + len(absent_skills)
        if total_risks == 0:
            risk_level = "Low"
        elif total_risks <= 2:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return {
            "recommendation": recommendation,
            "emoji": emoji,
            "color": color,
            "confidence": score,
            "risk_level": risk_level
        }

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
                        # Extract skills from JD once
                        skills = extract_skills_from_jd(jd_text)

                        for cv in cv_files:
                            cv_text = read_pdf(cv) if cv.name.endswith(".pdf") else read_docx(cv)
                            sim_score = similarity_score(cv_text, jd_text)

                            # Get skill scores for radar chart
                            skill_scores = get_skill_scores(cv_text, jd_text, skills)
                            
                            # Extract skill status for badges
                            skill_status = extract_skill_status(cv_text, jd_text)

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
                                "evaluation": evaluation,
                                "skill_scores": skill_scores,
                                "skills": skills,
                                "skill_status": skill_status
                            })

                    results = sorted(results, key=lambda x: x["score"], reverse=True)

                    st.success("Evaluation Completed")

                    # Create DataFrame and Plotly chart
                    df = pd.DataFrame(results)
                    df = df.rename(columns={"name": "Candidate", "score": "Score"})
                    
                    # Executive KPI
                    st.markdown("### Executive KPI")
                    
                    # Get top 5 candidates
                    top_5_candidates = df.nlargest(5, 'Score')
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    col1.metric("Total Candidates", len(df))
                    col2.metric("Average Match", f"{df['Score'].mean():.1f}%")
                    col3.metric("Top Score", f"{df['Score'].max():.1f}%")
                    col4.metric("Top 5 Candidates", f"{len(top_5_candidates)}")
                    
                    # Display top 5 candidates list
                    if len(top_5_candidates) > 0:
                        st.markdown("**Top 5 Candidates:**")
                        for idx, (_, row) in enumerate(top_5_candidates.iterrows(), 1):
                            st.markdown(f"{idx}. **{row['Candidate']}** - {row['Score']:.1f}%")
                    
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
                            # Get skill status for recommendation
                            skill_status = r.get("skill_status", {})
                            missing_skills = skill_status.get("missing", [])
                            absent_skills = skill_status.get("absent", [])
                            strong_skills = skill_status.get("strong", [])
                            
                            # Get all scores for relative comparison
                            all_scores = [res['score'] for res in results]
                            
                            # Get hire recommendation (with relative comparison)
                            hire_rec = get_hire_recommendation(
                                r['score'], 
                                missing_skills, 
                                absent_skills,
                                all_scores=all_scores
                            )
                            
                            # Display Hire Recommendation Card
                            card_html = f"""
                            <div style='
                                background: {hire_rec["color"]};
                                padding: 20px;
                                border-radius: 12px;
                                color: white;
                                margin-bottom: 20px;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            '>
                                <h3 style='margin: 0 0 10px 0; color: white; font-size: 1.5em;'>
                                    {hire_rec["emoji"]} {hire_rec["recommendation"]}
                                </h3>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                            
                            # Skill Radar Chart - HIDDEN FOR NOW
                            # st.markdown("#### Skill Radar Chart")
                            # skills = r.get("skills", [])
                            # skill_scores = r.get("skill_scores", {})
                            # 
                            # if skills and skill_scores:
                            #     # Prepare data for radar chart
                            #     r_values = [skill_scores.get(skill, 0) for skill in skills]
                            #     
                            #     fig = go.Figure()
                            #     
                            #     fig.add_trace(go.Scatterpolar(
                            #         r=r_values,
                            #         theta=skills,
                            #         fill='toself',
                            #         name=r['name']
                            #     ))
                            #     
                            #     fig.update_layout(
                            #         polar=dict(
                            #             radialaxis=dict(
                            #                 visible=True,
                            #                 range=[0, 100]
                            #             )
                            #         ),
                            #         showlegend=False,
                            #         height=400
                            #     )
                            #     
                            #     st.plotly_chart(fig, use_container_width=True)
                            
                            st.markdown("---")
                            
                            # Display Skill Risk Badges
                            
                            if missing_skills or absent_skills or strong_skills:
                                st.markdown("#### Skill Assessment")
                                
                                badges_html = ""
                                
                                # Strong skills (green)
                                for skill in strong_skills:
                                    badges_html += f"""
                                    <span style='background:#16a34a;padding:6px 12px;border-radius:20px;color:white;margin:4px;display:inline-block;font-size:0.9em;'>
                                        🟢 Strong {skill}
                                    </span>
                                    """
                                
                                # Missing skills (yellow)
                                for skill in missing_skills:
                                    badges_html += f"""
                                    <span style='background:#eab308;padding:6px 12px;border-radius:20px;color:white;margin:4px;display:inline-block;font-size:0.9em;'>
                                        🟡 Missing {skill}
                                    </span>
                                    """
                                
                                # Absent skills (red)
                                for skill in absent_skills:
                                    badges_html += f"""
                                    <span style='background:#dc2626;padding:6px 12px;border-radius:20px;color:white;margin:4px;display:inline-block;font-size:0.9em;'>
                                        🔴 No {skill}
                                    </span>
                                    """
                                
                                st.markdown(badges_html, unsafe_allow_html=True)
                                st.markdown("---")
                            
                            st.markdown("#### Detailed Evaluation")
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