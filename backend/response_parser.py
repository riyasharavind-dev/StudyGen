import json
import re


class AIResponseParser:

    @staticmethod
    def parse_json(response: str) -> dict:

        if not response:
            raise ValueError(
                "AI returned an empty response."
            )

        text = response.strip()

        # Remove Markdown code fences if the model
        # returns ```json ... ```

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        text = text.strip()

        # Direct JSON parsing

        try:

            data = json.loads(text)

            if not isinstance(data, dict):

                raise ValueError(
                    "AI response must be a JSON object."
                )

            return data

        except json.JSONDecodeError:
            pass

        # Try extracting the first JSON object

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "AI response does not contain valid JSON."
            )

        json_text = text[start:end + 1]

        try:

            data = json.loads(json_text)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"Invalid JSON returned by AI: {error}"
            )

        if not isinstance(data, dict):

            raise ValueError(
                "AI response must be a JSON object."
            )

        return data


    # =====================================================
    # MCQ VALIDATION
    # =====================================================

    @staticmethod
    def validate_mcq(data: dict) -> dict:

        if "questions" not in data:

            raise ValueError(
                "MCQ response is missing 'questions'."
            )

        questions = data["questions"]

        if not isinstance(questions, list):

            raise ValueError(
                "'questions' must be a list."
            )

        validated = []

        for index, question in enumerate(
            questions,
            start=1,
        ):

            if not isinstance(question, dict):

                raise ValueError(
                    f"Question {index} is invalid."
                )

            required = [
                "question",
                "options",
                "correct_answer",
                "explanation",
            ]

            for field in required:

                if field not in question:

                    raise ValueError(
                        f"Question {index} "
                        f"is missing '{field}'."
                    )

            options = question["options"]

            if not isinstance(options, dict):

                raise ValueError(
                    f"Question {index} "
                    "'options' must be an object."
                )

            for option in ["A", "B", "C", "D"]:

                if option not in options:

                    raise ValueError(
                        f"Question {index} "
                        f"is missing option {option}."
                    )

            correct = str(
                question["correct_answer"]
            ).upper().strip()

            if correct not in {
                "A",
                "B",
                "C",
                "D",
            }:

                raise ValueError(
                    f"Question {index} "
                    "has an invalid correct answer."
                )

            validated.append({

                "id": index,

                "question": str(
                    question["question"]
                ),

                "options": {
                    "A": str(options["A"]),
                    "B": str(options["B"]),
                    "C": str(options["C"]),
                    "D": str(options["D"]),
                },

                "correct_answer": correct,

                "explanation": str(
                    question["explanation"]
                ),
            })

        return {

            "topic": data.get(
                "topic",
                "",
            ),

            "difficulty": data.get(
                "difficulty",
                "medium",
            ),

            "questions": validated,
        }


    # =====================================================
    # FLASHCARD VALIDATION
    # =====================================================

    @staticmethod
    def validate_flashcards(
        data: dict,
    ) -> dict:

        if "flashcards" not in data:

            raise ValueError(
                "Response is missing 'flashcards'."
            )

        cards = data["flashcards"]

        if not isinstance(cards, list):

            raise ValueError(
                "'flashcards' must be a list."
            )

        validated = []

        for index, card in enumerate(
            cards,
            start=1,
        ):

            if not isinstance(card, dict):

                raise ValueError(
                    f"Flashcard {index} is invalid."
                )

            if (
                "question" not in card
                or
                "answer" not in card
            ):

                raise ValueError(
                    f"Flashcard {index} "
                    "is incomplete."
                )

            validated.append({

                "id": index,

                "question": str(
                    card["question"]
                ),

                "answer": str(
                    card["answer"]
                ),
            })

        return {

            "topic": data.get(
                "topic",
                "",
            ),

            "flashcards": validated,
        }