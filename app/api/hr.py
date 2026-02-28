from flask import Blueprint, request
from pydantic import ValidationError
from app.middleware.auth import require_auth, require_role
from app.services.hr_service import HRService
from app.utils.response import success_response, error_response, validation_error_response
from app.schemas.cv_evaluation import CVEvaluationRequest, CVEvaluationResponse
from app.schemas.policy import PolicyUploadRequest, PolicyQuestionRequest, PolicyQuestionResponse
from app.schemas.technical import (
    TechnicalQuestionGenerateRequest, TechnicalQuestionResponse,
    TechnicalAnswerEvaluateRequest, TechnicalAnswerEvaluateResponse
)

bp = Blueprint('hr', __name__)
hr_service = HRService()


@bp.route('/cv/evaluate', methods=['POST'])
@require_auth
def evaluate_cvs():
    """Evaluate multiple CVs against job description"""
    try:
        # Get job description from form data
        jd_text = request.form.get('job_description')
        if not jd_text:
            return error_response("job_description is required", status_code=400)
        
        # Get CV files
        cv_files = request.files.getlist('cv_files')
        if not cv_files or not any(f.filename for f in cv_files):
            return error_response("At least one CV file is required", status_code=400)
        
        # Evaluate CVs
        result = hr_service.evaluate_cvs(cv_files, jd_text)
        
        # Format response
        response_data = CVEvaluationResponse(
            results=result['results'],
            executive_kpis=result['executive_kpis']
        )
        
        return success_response(data=response_data.dict(), message="CV evaluation completed")
    
    except Exception as e:
        return error_response(f"Error evaluating CVs: {str(e)}", status_code=500)


@bp.route('/policy/upload', methods=['POST'])
@require_auth
@require_role('HR Manager')
def upload_policies():
    """Upload policy documents"""
    try:
        policy_files = request.files.getlist('policy_files')
        if not policy_files or not any(f.filename for f in policy_files):
            return error_response("At least one policy file is required", status_code=400)
        
        user_id = request.g.user_id
        result = hr_service.upload_policies(policy_files, user_id)
        
        return success_response(data=result, message=result['message'])
    
    except Exception as e:
        return error_response(f"Error uploading policies: {str(e)}", status_code=500)


@bp.route('/policy/ask', methods=['POST'])
@require_auth
def ask_policy_question():
    """Ask question about HR policies"""
    try:
        question_data = PolicyQuestionRequest(**request.json)
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return validation_error_response(errors)
    
    try:
        answer = hr_service.ask_policy_question(question_data.question)
        
        response_data = PolicyQuestionResponse(answer=answer)
        return success_response(data=response_data.dict(), message="Policy question answered")
    
    except Exception as e:
        return error_response(f"Error answering policy question: {str(e)}", status_code=500)


@bp.route('/technical/generate-questions', methods=['POST'])
@require_auth
@require_role('HR Manager')
def generate_technical_questions():
    """Generate technical interview questions"""
    try:
        # Get job description from form data
        jd_text = request.form.get('job_description')
        if not jd_text:
            return error_response("job_description is required", status_code=400)
        
        # Get CV file
        cv_file = request.files.get('cv_file')
        if not cv_file or not cv_file.filename:
            return error_response("CV file is required", status_code=400)
        
        # Generate questions
        questions = hr_service.generate_technical_questions(cv_file, jd_text)
        
        response_data = TechnicalQuestionResponse(questions=questions)
        return success_response(data=response_data.dict(), message="Technical questions generated")
    
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return error_response(f"Error generating questions: {str(e)}", status_code=500)


@bp.route('/technical/evaluate-answers', methods=['POST'])
@require_auth
@require_role('HR Manager')
def evaluate_technical_answers():
    """Evaluate technical interview answers"""
    try:
        eval_data = TechnicalAnswerEvaluateRequest(**request.json)
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return validation_error_response(errors)
    
    try:
        result = hr_service.evaluate_technical_answers(
            eval_data.questions,
            eval_data.answers
        )
        
        response_data = TechnicalAnswerEvaluateResponse(
            evaluations=result['evaluations'],
            total_score=result['total_score'],
            max_score=result['max_score'],
            overall_feedback=result['overall_feedback']
        )
        
        return success_response(data=response_data.dict(), message="Technical evaluation completed")
    
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return error_response(f"Error evaluating answers: {str(e)}", status_code=500)
