from pydantic import BaseModel


class CandidateInfoSchema(BaseModel):
    first_name: str
    second_name: str
    job_title: str


class GeneratedQuestionsSchema(BaseModel):
    candidate_id: str
    questions: list[str]


class CandidateResponseSchema(BaseModel):
    response: str


class ScoreAndCommentSchema(BaseModel):
    score: int
    comment: str


class ResponseEvaluationSchema(BaseModel):
    scores: list[ScoreAndCommentSchema]


class ValidationResultSchema(ResponseEvaluationSchema):
    questions: list[str]
    response: str
    scores: list[int]
    comments: list[str]
    feedback: str
