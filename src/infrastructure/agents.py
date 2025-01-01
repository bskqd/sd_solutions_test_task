import json

from openai import AsyncOpenAI

from dto import ResponseEvaluationAgentResult, ValidationAgentResult


class GenerateQuestionsAgent:
    def __init__(self, client: AsyncOpenAI):
        self._client = client
        self._system_content = (
            """
            You are an HR assistant tasked with generating interview questions tailored to the candidate's job title.
            The questions should focus on practical technical requirements, skills, and knowledge essential for 
            similar roles. Ensure the questions are clear, relevant, and appropriate for assessing the candidate's 
            qualifications for the position.
            
            Output format is a valid JSON string like:
            
            ["1. [Insert Question]", "2. [Insert Question]"]
            """
        )

    async def generate_questions(self, job_title: str) -> list[str]:
        prompt = f"Generate 3 interview questions for a {job_title}."
        result = await self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": self._system_content}, {"role": "user", "content": prompt}]
        )
        questions = result.choices[0].message.content.strip()
        return json.loads(questions)


class ResponseEvaluationAgent:
    def __init__(self, client: AsyncOpenAI):
        self._client = client
        self._system_content = (
            """
            You are an interview evaluator responsible for scoring the candidate's responses to interview questions.
            For each question, assign a score from 1 to 5 based on the quality of the response and provide a brief
            comment explaining the rationale for the score. Take the candidate's job title into account to ensure the
            evaluation is aligned with the expectations and requirements of the role, do not take any grammar or 
            spelling mistakes into account, decide only based on technical side.
            
            Output format is a valid JSON string like:
            [
                {
                    "score": [Insert Integer Score],
                    "comment": [Insert Comment]
                },
                {
                    "score": [Insert Integer Score],
                    "comment": [Insert Comment]
                }
                
                [Repeat for all responses]
            ]
            """
        )

    async def evaluate_response(
            self,
            job_title: str,
            questions: list[str],
            response: str,
    ) -> list[ResponseEvaluationAgentResult]:
        prompt = (
            f"Job Title: {job_title}\n"
            f"Questions: {questions}\n"
            f"Response: {response}\n"
        )
        result = await self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": self._system_content}, {"role": "user", "content": prompt}]
        )
        return json.loads(result.choices[0].message.content.strip())


class ValidationAgent:
    def __init__(self, client: AsyncOpenAI):
        self._client = client
        self._system_content = (
            """
            You are a Validation Agent responsible for reviewing and confirming the accuracy of interview evaluation 
            scores and providing meaningful feedback, do not take any grammar or spelling mistakes into account, 
            decide only based on technical side. Your role is to:

            1. Review the provided questions, candidate responses, and initial scores with comments.
            2. Ensure the scores are fair and consistent based on the quality of the responses.
            3. Adjust scores if necessary and provide justification for changes.
            4. Generate a final summary report that includes:
               - Final Scores (on a scale of 1 to 5)
               - Comment for each response
               - Overall performance feedback based on the scores.
            
            Be concise but clear, ensuring your feedback is constructive and helpful for the candidate.
            
            Output is a valid JSON string like:
            
            {
                "scores": [
                    {
                        "score": [Insert Integer Score],
                        "comment": [Insert Comment]
                    },
                    {
                        "score": [Insert Integer Score],
                        "comment": [Insert Comment]
                    }
                    
                    [Repeat for all responses]
                ],
                "feedback": [Insert summary, e.g., "Excellent", "Good", or "Needs Improvement"]
            }
            """
        )

    async def validate_scores(
            self,
            job_title: str,
            questions: list[str],
            response: str,
            scores: list[int],
            comments: list[str],
    ) -> ValidationAgentResult:
        prompt = (
            f"Job Title: {job_title}\n"
            f"Questions: {questions}\n"
            f"Response: {response}\n"
            f"Scores: {scores}\n"
            f"Comments: {comments}"
        )
        result = await self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": self._system_content}, {"role": "user", "content": prompt}]
        )
        return json.loads(result.choices[0].message.content.strip())
