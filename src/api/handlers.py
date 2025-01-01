from typing import Annotated

from fastapi import APIRouter, Depends, Header

from api.schemas import (
    CandidateInfoSchema, GeneratedQuestionsSchema, CandidateResponseSchema, ResponseEvaluationSchema,
    ValidationResultSchema,
)
from dependencies import Stub
from services import GenerateQuestionsService, EvaluateResponsesService, ValidationService

router = APIRouter()


@router.get("/generate_questions", response_model=GeneratedQuestionsSchema)
async def generate_questions(
        candidate_info: CandidateInfoSchema,
        generate_questions_service: GenerateQuestionsService = Depends(Stub(GenerateQuestionsService)),
):
    generated_questions_result = await generate_questions_service.generate_questions(
        candidate_info.first_name, candidate_info.second_name, candidate_info.job_title,
    )
    return GeneratedQuestionsSchema(
        candidate_id=generated_questions_result.candidate_id,
        questions=generated_questions_result.questions,
    )


@router.post("/evaluate_responses", response_model=ResponseEvaluationSchema)
async def evaluate_responses(
        response: CandidateResponseSchema,
        candidate_id: Annotated[str | None, Header()] = None,
        response_evaluation_service: EvaluateResponsesService = Depends(Stub(EvaluateResponsesService)),
):
    result = await response_evaluation_service.evaluate_response(candidate_id, response.response)
    return ResponseEvaluationSchema(scores=result)


@router.post("/validate_scores", response_model=ValidationResultSchema)
async def validate_scores(
        candidate_id: Annotated[str | None, Header()] = None,
        validation_service: ValidationService = Depends(Stub(ValidationService)),
):
    result = await validation_service.validate(candidate_id)
    return ValidationResultSchema(
        questions=result.questions,
        response=result.candidate_response,
        scores=result.scores,
        comments=result.response_comments,
        feedback=result.feedback,
    )
