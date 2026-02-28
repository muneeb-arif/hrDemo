import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from app.utils.openai_client import get_openai_client
from app.repositories.policy_document_repository import PolicyDocumentRepository
from app.utils.file_processor import process_file, process_multiple_files
from werkzeug.datastructures import FileStorage


class HRService:
    """Service for HR AI Platform operations"""
    
    def __init__(self):
        self.client = get_openai_client()
        self.policy_repo = PolicyDocumentRepository()
    
    def _ask_llm(self, prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
        """Helper to call OpenAI LLM"""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity score between two texts"""
        tfidf = TfidfVectorizer(stop_words="english")
        matrix = tfidf.fit_transform([text1, text2])
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(score * 100, 2)
    
    def extract_skills_from_jd(self, jd_text: str) -> List[str]:
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
        response = self._ask_llm(prompt)
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            if response.startswith("["):
                skills = json.loads(response)
                return [s.strip() for s in skills if s.strip()]
        except:
            pass
        # Fallback: return default skills
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
    
    def get_skill_scores(self, cv_text: str, jd_text: str, skills: List[str]) -> Dict[str, float]:
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
        response = self._ask_llm(prompt)
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            if response.startswith("{"):
                scores = json.loads(response)
                return {skill: scores.get(skill, 0) for skill in skills}
        except:
            pass
        return {skill: 50 for skill in skills}
    
    def extract_skill_status(self, cv_text: str, jd_text: str) -> Dict[str, List[str]]:
        """Extract missing skills, absent skills, and strong skills from CV vs JD"""
        prompt = f"""
        Analyze the candidate's CV against the Job Description.
        Return ONLY a JSON object with three arrays:
        - "missing": skills mentioned in JD but weak/limited in CV
        - "absent": skills required in JD but completely missing from CV
        - "strong": skills that are strong/prominent in CV
        
        Return only specific technology/tool names (e.g., "TypeScript", "Vue.js", "React", "Docker", etc.)
        Keep skill names concise (1-3 words max).
        
        CV:
        {cv_text[:2000]}
        
        Job Description:
        {jd_text[:2000]}
        
        Return format: {{"missing": ["Skill1", "Skill2"], "absent": ["Skill3"], "strong": ["Skill4", "Skill5"]}}
        """
        response = self._ask_llm(prompt)
        try:
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
        return {"missing": [], "absent": [], "strong": []}
    
    def get_hire_recommendation(self, score: float, missing_skills: List[str], 
                                absent_skills: List[str], all_scores: List[float] = None) -> Dict:
        """Determine hire recommendation based on score, missing skills, and relative ranking"""
        if all_scores and len(all_scores) > 1:
            avg_score = sum(all_scores) / len(all_scores)
            max_score = max(all_scores)
            
            if score >= max_score * 0.9:
                recommendation = "Strong Hire"
                emoji = "🟢"
                color = "#16a34a"
            elif score >= avg_score * 1.2 or score >= 60:
                recommendation = "Consider"
                emoji = "🟡"
                color = "#eab308"
            elif score >= avg_score:
                recommendation = "Consider"
                emoji = "🟡"
                color = "#eab308"
            else:
                recommendation = "Not Recommended"
                emoji = "🔴"
                color = "#dc2626"
        else:
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
    
    def evaluate_cvs(self, cv_files: List[FileStorage], jd_text: str) -> Dict:
        """Evaluate multiple CVs against job description"""
        # Extract skills from JD once
        skills = self.extract_skills_from_jd(jd_text)
        
        # Process all CV files
        cv_results = process_multiple_files(cv_files)
        
        results = []
        for filename, cv_text in cv_results:
            if cv_text.startswith("Error"):
                continue  # Skip files that failed to process
            
            sim_score = self.similarity_score(cv_text, jd_text)
            skill_scores = self.get_skill_scores(cv_text, jd_text, skills)
            skill_status = self.extract_skill_status(cv_text, jd_text)
            
            # Get detailed evaluation
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
            evaluation = self._ask_llm(prompt)
            
            results.append({
                "name": filename,
                "score": sim_score,
                "evaluation": evaluation,
                "skill_scores": skill_scores,
                "skills": skills,
                "skill_status": skill_status
            })
        
        # Sort by score descending
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        # Calculate executive KPIs
        if results:
            scores = [r["score"] for r in results]
            executive_kpis = {
                "total_candidates": len(results),
                "average_match": round(sum(scores) / len(scores), 1),
                "top_score": max(scores),
                "top_5_count": min(5, len(results))
            }
        else:
            executive_kpis = {
                "total_candidates": 0,
                "average_match": 0,
                "top_score": 0,
                "top_5_count": 0
            }
        
        # Add hire recommendations
        all_scores = [r["score"] for r in results]
        for result in results:
            skill_status = result.get("skill_status", {})
            missing_skills = skill_status.get("missing", [])
            absent_skills = skill_status.get("absent", [])
            result["hire_recommendation"] = self.get_hire_recommendation(
                result["score"], missing_skills, absent_skills, all_scores
            )
        
        return {
            "results": results,
            "executive_kpis": executive_kpis
        }
    
    def upload_policies(self, policy_files: List[FileStorage], user_id: int) -> Dict:
        """Upload policy documents"""
        processed_files = process_multiple_files(policy_files)
        document_ids = []
        
        for filename, content in processed_files:
            if content.startswith("Error"):
                continue
            
            policy_doc = self.policy_repo.create(
                filename=filename,
                content=content,
                uploaded_by=user_id
            )
            document_ids.append(policy_doc.id)
        
        return {
            "message": f"{len(document_ids)} policy document(s) uploaded successfully",
            "document_count": len(document_ids),
            "document_ids": document_ids
        }
    
    def ask_policy_question(self, question: str) -> str:
        """Ask question about HR policies"""
        policies_text = self.policy_repo.get_all_content()
        
        if not policies_text:
            return "HR policy documents not available. Contact HR."
        
        prompt = f"""
        Answer ONLY using the HR policies below.
        If information not present, say:
        "Policy does not specify this."
        
        POLICIES:
        {policies_text}
        
        QUESTION:
        {question}
        """
        
        answer = self._ask_llm(prompt)
        return answer
    
    def generate_technical_questions(self, cv_file: FileStorage, jd_text: str) -> List[str]:
        """Generate technical interview questions from CV and JD"""
        filename, cv_text = process_file(cv_file)
        
        if cv_text.startswith("Error"):
            raise ValueError(f"Error processing CV: {cv_text}")
        
        prompt = f"""
        You are a technical interviewer.
        
        Based on the candidate CV and Job Description,
        generate 5 technical interview questions.
        Questions should increase in difficulty.
        Number them clearly from 1 to 5.
        
        Candidate CV:
        {cv_text}
        
        Job Description:
        {jd_text}
        """
        
        questions_text = self._ask_llm(prompt)
        
        # Parse questions
        questions_list = [
            q.strip() for q in questions_text.split("\n")
            if q.strip() and (q.strip()[0].isdigit() or q.strip().startswith("Q"))
        ]
        
        # Clean up question numbers
        cleaned_questions = []
        for q in questions_list:
            # Remove leading numbers, Q1, Q2, etc.
            q = q.lstrip("0123456789. )Qq-")
            if q.strip():
                cleaned_questions.append(q.strip())
        
        # Return top 5
        return cleaned_questions[:5]
    
    def evaluate_technical_answers(self, questions: List[str], answers: List[str]) -> Dict:
        """Evaluate technical interview answers"""
        if len(questions) != len(answers):
            raise ValueError("Number of questions and answers must match")
        
        evaluations = []
        total_score = 0
        
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            eval_prompt = f"""
            Evaluate the candidate's answer to the following technical question.
            Provide a score from 0 to 20 and a short feedback.
            
            Question:
            {q}
            
            Candidate Answer:
            {a}
            """
            
            result = self._ask_llm(eval_prompt)
            
            # Try to extract score from result
            score = 10  # Default score
            try:
                # Look for score in format "Score: 15" or "15/20"
                import re
                score_match = re.search(r'(\d+)\s*(?:/|out of|of)\s*20', result, re.IGNORECASE)
                if score_match:
                    score = float(score_match.group(1))
                else:
                    score_match = re.search(r'Score[:\s]+(\d+)', result, re.IGNORECASE)
                    if score_match:
                        score = float(score_match.group(1))
            except:
                pass
            
            evaluations.append({
                "question_number": i,
                "question": q,
                "answer": a,
                "score": min(20, max(0, score)),
                "feedback": result
            })
            total_score += score
        
        max_score = len(questions) * 20
        
        # Generate overall feedback
        overall_feedback = f"Technical Evaluation Completed. Total Score: {total_score:.1f} / {max_score:.1f}"
        
        return {
            "evaluations": evaluations,
            "total_score": round(total_score, 1),
            "max_score": max_score,
            "overall_feedback": overall_feedback
        }
