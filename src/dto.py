import typing
from dataclasses import dataclass


@dataclass(slots=True)
class GeneratedQuestionsResult:
    candidate_id: str
    questions: list[str]


@dataclass(slots=True)
class SharedContextCandidateFullInfo:
    candidate_id: str
    first_name: str
    second_name: str
    job_title: str
    questions: list[str]
    candidate_response: str
    scores: list[int]
    response_comments: list[str]
    feedback: str


class ResponseEvaluationAgentResult(typing.TypedDict):
    score: int
    comment: str


class ValidationAgentResult(typing.TypedDict):
    scores: list[ResponseEvaluationAgentResult]
    feedback: str
