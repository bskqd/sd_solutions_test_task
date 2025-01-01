import json

import redis.asyncio as redis

from dto import SharedContextCandidateFullInfo, ResponseEvaluationAgentResult


class SharedContext:
    def __init__(self, redis_connection: redis.Redis):
        self._redis_connection = redis_connection

    async def get_full_candidate_info(self, candidate_id: str) -> SharedContextCandidateFullInfo:
        info = await self._redis_connection.hgetall(candidate_id)
        return SharedContextCandidateFullInfo(
            candidate_id=candidate_id,
            first_name=info.get(b"first_name", b"").decode(),
            second_name=info.get(b"second_name", b"").decode(),
            job_title=info.get(b"job_title", b"").decode(),
            questions=json.loads(info.get(b"questions", "[]")),
            candidate_response=info.get(b"candidate_response", b"").decode(),
            scores=json.loads(info.get(b"scores", "[]")),
            response_comments=json.loads(info.get(b"response_comments", "[]")),
            feedback=info.get(b"feedback", b"").decode(),
        )

    async def delete_candidate_info(self, candidate_id: str):
        await self._redis_connection.delete(candidate_id)

    async def save_candidate_info_and_questions(
            self,
            candidate_id: str,
            first_name: str,
            second_name: str,
            job_title: str,
            questions: list[str],
    ):
        await self.delete_candidate_info(candidate_id)
        await self._redis_connection.hset(
            candidate_id,
            mapping={
                "first_name": first_name,
                "second_name": second_name,
                "job_title": job_title,
                "questions": json.dumps(questions),
            }
        )

    async def save_response_scores_and_comments(
            self,
            candidate_id: str,
            response: str,
            scores_and_comments: list[ResponseEvaluationAgentResult],
    ):
        scores = []
        comments = []
        for result in scores_and_comments:
            scores.append(result["score"])
            comments.append(result["comment"])
        await self._redis_connection.hset(
            candidate_id,
            mapping={
                "candidate_response": response,
                "scores": json.dumps(scores),
                "response_comments": json.dumps(comments),
            }
        )

    async def save_feedback(self, candidate_id: str, feedback: str):
        await self._redis_connection.hset(candidate_id, "feedback", feedback)
