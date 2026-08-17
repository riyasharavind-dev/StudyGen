import uuid
from typing import Any


class QuizStore:

    def __init__(self):
        self.quizzes: dict[str, dict[str, Any]] = {}

    def create(
        self,
        questions: list[dict[str, Any]],
        topic: str,
        difficulty: str,
    ) -> str:

        quiz_id = str(uuid.uuid4())

        self.quizzes[quiz_id] = {
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
        }

        return quiz_id

    def get(
        self,
        quiz_id: str,
    ) -> dict[str, Any] | None:

        return self.quizzes.get(quiz_id)

    def delete(
        self,
        quiz_id: str,
    ):

        self.quizzes.pop(
            quiz_id,
            None,
        )