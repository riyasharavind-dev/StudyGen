from typing import Any


class QuizEngine:

    def evaluate(
        self,
        questions: list[dict[str, Any]],
        answers: dict[str, str],
    ) -> dict:

        if not questions:
            raise ValueError(
                "No quiz questions provided."
            )

        results = []

        correct_count = 0

        for index, question in enumerate(
            questions,
            start=1,
        ):

            question_id = str(
                question.get(
                    "id",
                    index,
                )
            )

            correct_answer = str(
                question.get(
                    "correct_answer",
                    "",
                )
            ).upper().strip()

            user_answer = str(
                answers.get(
                    question_id,
                    "",
                )
            ).upper().strip()

            is_correct = (
                user_answer == correct_answer
            )

            if is_correct:
                correct_count += 1

            results.append(
                {
                    "id": question_id,
                    "question": question.get(
                        "question",
                        "",
                    ),
                    "selected_answer": (
                        user_answer
                        if user_answer
                        else None
                    ),
                    "correct_answer": (
                        correct_answer
                    ),
                    "is_correct": is_correct,
                    "explanation": question.get(
                        "explanation",
                        "",
                    ),
                }
            )

        total = len(questions)

        percentage = round(
            (correct_count / total) * 100,
            2,
        )

        return {
            "total_questions": total,
            "correct_answers": correct_count,
            "wrong_answers": (
                total - correct_count
            ),
            "score": correct_count,
            "percentage": percentage,
            "results": results,
        }