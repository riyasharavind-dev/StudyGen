from ai_router import AIRouter


class StudyGenerator:

    def __init__(self, router: AIRouter):
        self.router = router

    def _generate(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
    ):

        return self.router.generate(
            prompt=prompt,
            preferred_provider=provider,
            model=model,
        )

    # =====================================================
    # GENERAL STUDY GENERATOR
    # =====================================================

    def generate(
        self,
        topic: str,
        content_type: str = "explanation",
        difficulty: str = "medium",
        count: int = 5,
        provider: str | None = None,
        model: str | None = None,
    ):

        if not topic.strip():
            raise ValueError(
                "Topic cannot be empty."
            )

        allowed_types = {
            "explanation",
            "summary",
            "notes",
            "mcq",
            "flashcards",
            "quiz",
        }

        content_type = content_type.lower().strip()

        if content_type not in allowed_types:
            raise ValueError(
                "Unsupported content type."
            )

        if count < 1:
            raise ValueError(
                "Count must be at least 1."
            )

        if content_type == "mcq":
            return self.generate_mcq(
                topic=topic,
                difficulty=difficulty,
                count=count,
                provider=provider,
                model=model,
            )

        if content_type == "flashcards":
            return self.generate_flashcards(
                topic=topic,
                difficulty=difficulty,
                count=count,
                provider=provider,
                model=model,
            )

        if content_type == "quiz":
            return self.generate_quiz(
                topic=topic,
                difficulty=difficulty,
                count=count,
                provider=provider,
                model=model,
            )

        prompt = f"""
You are StudyGen, an AI study assistant.

Topic:
{topic}

Difficulty:
{difficulty}

Create {content_type} study material.

For explanation:
Explain the topic clearly and logically.

For summary:
Create concise revision-focused content.

For notes:
Create structured academic notes.

Use headings and bullet points where useful.

Keep the answer accurate, clear,
student-friendly, and suitable for examination.
"""

        return self._generate(
            prompt=prompt,
            provider=provider,
            model=model,
        )

    # =====================================================
    # NOTES
    # =====================================================

    def generate_notes(
        self,
        topic: str,
        level: str = "college",
        provider: str | None = None,
        model: str | None = None,
    ):

        if not topic.strip():
            raise ValueError(
                "Topic cannot be empty."
            )

        prompt = f"""
You are StudyGen.

Create concise but complete academic
revision notes.

Topic:
{topic}

Academic Level:
{level}

Use these sections:

# Definition

# Core Concepts

# Detailed Notes

# Key Points

# Advantages

# Disadvantages

# Applications

# Important Terms

# Quick Revision

Keep the notes useful for examination preparation.
"""

        return self._generate(
            prompt=prompt,
            provider=provider,
            model=model,
        )

    # =====================================================
    # MCQ
    # =====================================================

    def generate_mcq(
        self,
        topic: str,
        difficulty: str = "medium",
        count: int = 5,
        provider: str | None = None,
        model: str | None = None,
    ):

        prompt = f"""
You are StudyGen's MCQ generator.

Create exactly {count} multiple-choice questions.

Topic:
{topic}

Difficulty:
{difficulty}

Return ONLY valid JSON.

Do not use Markdown.

Use exactly this structure:

{{
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "question": "Question text",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Short explanation"
    }}
  ]
}}

Rules:

1. Create exactly {count} questions.
2. Every question must have four options.
3. Only one option can be correct.
4. correct_answer must be A, B, C, or D.
5. Explanations must be concise.
6. Questions must be relevant to the topic.
7. Avoid duplicate questions.
8. Return JSON only.
"""

        return self._generate(
            prompt=prompt,
            provider=provider,
            model=model,
        )

    # =====================================================
    # FLASHCARDS
    # =====================================================

    def generate_flashcards(
        self,
        topic: str,
        difficulty: str = "medium",
        count: int = 5,
        provider: str | None = None,
        model: str | None = None,
    ):

        prompt = f"""
You are StudyGen's flashcard generator.

Create exactly {count} flashcards.

Topic:
{topic}

Difficulty:
{difficulty}

Return ONLY valid JSON.

Use:

{{
  "topic": "{topic}",
  "flashcards": [
    {{
      "id": 1,
      "question": "Question",
      "answer": "Answer"
    }}
  ]
}}

Rules:

1. Create exactly {count} flashcards.
2. Questions must test important concepts.
3. Answers must be concise.
4. Avoid duplicate cards.
5. Return JSON only.
"""

        return self._generate(
            prompt=prompt,
            provider=provider,
            model=model,
        )

    # =====================================================
    # QUIZ
    # =====================================================

    def generate_quiz(
        self,
        topic: str,
        difficulty: str = "medium",
        count: int = 10,
        provider: str | None = None,
        model: str | None = None,
    ):

        prompt = f"""
You are StudyGen's quiz generator.

Create exactly {count} multiple-choice questions.

Topic:
{topic}

Difficulty:
{difficulty}

Return ONLY valid JSON.

Use:

{{
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "question": "Question",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Explanation"
    }}
  ]
}}

Rules:

1. Exactly {count} questions.
2. Four options per question.
3. One correct answer.
4. No duplicate questions.
5. Return JSON only.
"""

        return self._generate(
            prompt=prompt,
            provider=provider,
            model=model,
        )