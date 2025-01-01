# How to run

1. Clone the repo: `git clone https://github.com/bskqd/sd_solutions_test_task.git`
2. Go into project directory: `cd sd_solutions_test_task`
3. Create `.env` file with variables provided in [.env.example](.env.example)
4. Make sure that ports `8000`, `9000`, `9001` aren't already occupied by other processes on your PC
5. Run docker compose: `docker-compose up -d --build`

# Approach to solving the task

I created a FastAPI application which has 3 endpoints responsible for orchestrating 3 main agents:
1. Question Generation: Dynamically generates interview questions.
2. Response Evaluation: Evaluates candidate responses.
3. Evaluation Validation: Validates the evaluation and logs the completed session.

All completed interview sessions are logged and stored in MinIO.

# Choice of framework and key decisions

1. **Python Framework**: As was mentioned in the task I chose `FastAPI` as the python framework for this task to have fully `async` API handlers.
2. **Shared Context**: I chose `Redis` for the shared context, convenient in memory DB for such purposes.
3. **LLM**: I chose `OpenAI` LLM as it was quite easy to understand and use as I don't have much of experience with any LLMs.
4. **Storage**: Integrated MinIO to provide a scalable and S3-compatible storage backend for file uploads as it was asked in the task.
5. **Candidate ID Generation**: Candidate IDs are generated based on a hash of the candidate's job title, first name, 
and last name, it allows for easy cleanup of incomplete interview sessions by overwriting existing data for the same
candidate in the shared context. Using UUID-like IDs would not allow this functionality. 
6. **Simplified Infrastructure**: All logs and full sessions' data are stored in the MinIO storage, avoiding the need for
additional infrastructure like DynamoDB.

# Challenges

The biggest challenge was working with the LLM, as I don't have much experience. I researched existing solutions and frameworks,
focusing on OpenAI's documentation. I tried different prompts to ensure the generated questions, evaluations, and 
validations met the task requirements. I adjusted output formats to make the data more structured and easier to work with.
