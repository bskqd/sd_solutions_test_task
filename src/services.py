import hashlib
import io
import json
import zoneinfo
from dataclasses import asdict
from datetime import datetime

from infrastructure.agents import GenerateQuestionsAgent, ResponseEvaluationAgent, ValidationAgent
from config import Config
from dto import GeneratedQuestionsResult, ResponseEvaluationAgentResult, SharedContextCandidateFullInfo
from infrastructure.files_storage import FilesStorage
from infrastructure.shared_context import SharedContext


class GenerateQuestionsService:
    def __init__(self, shared_context: SharedContext, generate_questions_agent: GenerateQuestionsAgent):
        self._agent = generate_questions_agent
        self._shared_context = shared_context

    async def generate_questions(self, first_name: str, second_name: str, job_title: str) -> GeneratedQuestionsResult:
        candidate_id = self._get_candidate_id(first_name, second_name, job_title)
        generated_questions = await self._agent.generate_questions(job_title)
        await self._shared_context.save_candidate_info_and_questions(
            candidate_id, first_name, second_name, job_title, generated_questions,
        )
        return GeneratedQuestionsResult(candidate_id=candidate_id, questions=generated_questions)

    def _get_candidate_id(self, first_name: str, second_name: str, job_title: str) -> str:
        encoded_str = f"{first_name}_{second_name}_{job_title}".encode("utf-8")
        hash_obj = hashlib.sha256(encoded_str)
        return hash_obj.hexdigest()


class EvaluateResponsesService:
    def __init__(self, shared_context: SharedContext, evaluate_responses_agent: ResponseEvaluationAgent):
        self._agent = evaluate_responses_agent
        self._shared_context = shared_context

    async def evaluate_response(self, candidate_id: str, response: str) -> list[ResponseEvaluationAgentResult]:
        candidate_info = await self._shared_context.get_full_candidate_info(candidate_id)
        result = await self._agent.evaluate_response(candidate_info.job_title, candidate_info.questions, response)
        await self._shared_context.save_response_scores_and_comments(candidate_id, response, result)
        return result


class ValidationService:
    def __init__(
            self,
            config: Config,
            shared_context: SharedContext,
            validation_agent: ValidationAgent,
            files_storage_client: FilesStorage,
    ):
        self._config = config
        self._agent = validation_agent
        self._shared_context = shared_context
        self._files_storage = files_storage_client

    async def validate(self, candidate_id: str) -> SharedContextCandidateFullInfo:
        candidate_info = await self._shared_context.get_full_candidate_info(candidate_id)
        result = await self._agent.validate_scores(
            candidate_info.job_title, candidate_info.questions, candidate_info.candidate_response,
            candidate_info.scores, candidate_info.response_comments,
        )
        await self._shared_context.save_response_scores_and_comments(
            candidate_id, candidate_info.candidate_response, result["scores"],
        )
        await self._shared_context.save_feedback(candidate_id, result["feedback"])
        candidate_info = await self._shared_context.get_full_candidate_info(candidate_id)
        current_datetime = datetime.now().astimezone(zoneinfo.ZoneInfo("UTC"))
        persistent_storage_candidate_info_url = await self._save_candidate_info_to_persistent_storage(
            candidate_info, current_datetime,
        )
        await self._save_session_log(candidate_info, current_datetime, persistent_storage_candidate_info_url)
        await self._shared_context.delete_candidate_info(candidate_id)
        return candidate_info

    async def _save_candidate_info_to_persistent_storage(
            self,
            candidate_info: SharedContextCandidateFullInfo,
            current_datetime: datetime,
    ) -> str:
        filename = f"{candidate_info.candidate_id}_{current_datetime.timestamp()}.json"
        json_data = json.dumps(asdict(candidate_info), indent=4).encode("utf-8")
        json_length = len(json_data)
        json_file = io.BytesIO(json_data)
        return await self._files_storage.put_object(
            bucket_name=self._config.PERSISTENT_DATA_BUCKET_NAME,
            object_name=filename,
            data=json_file,
            length=json_length,
            content_type="application/json",
        )

    async def _save_session_log(
            self,
            candidate_info: SharedContextCandidateFullInfo,
            current_datetime: datetime,
            persistent_storage_candidate_info_url: str,
    ):
        filename = f"{candidate_info.candidate_id}_{current_datetime.timestamp()}.json"
        data = {
            "candidate_id": candidate_info.candidate_id,
            "job_title": candidate_info.job_title,
            "timestamp": current_datetime.timestamp(),
            "url": persistent_storage_candidate_info_url,
        }
        json_data = json.dumps(data, indent=4).encode("utf-8")
        json_length = len(json_data)
        json_file = io.BytesIO(json_data)
        await self._files_storage.put_object(
            bucket_name=self._config.LOGS_BUCKET_NAME,
            object_name=filename,
            data=json_file,
            length=json_length,
            content_type="application/json",
        )
