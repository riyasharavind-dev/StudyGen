import json
import math
import re
from typing import Optional

from ai_router import AIRouter


class StudyMaterialProcessor:
    """
    Converts arbitrarily large extracted study material into AI-sized chunks.

    There is intentionally no 100,000-character input limit here.
    The material is split before it reaches a provider, then the partial
    results are merged/reduced in additional AI calls when necessary.
    """

    # Conservative character window. This is deliberately below common
    # context limits because different providers/models have different limits.
    CHUNK_SIZE = 24000
    CHUNK_OVERLAP = 600
    REDUCE_GROUP_SIZE = 18000

    def __init__(self, router: Optional[AIRouter] = None):
        self.router = router or AIRouter()

    def _clean(self, text: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", text.strip())

    def _split_material(self, material: str) -> list[str]:
        material = self._clean(material)
        if not material:
            return []

        if len(material) <= self.CHUNK_SIZE:
            return [material]

        paragraphs = re.split(r"\n\s*\n", material)
        chunks: list[str] = []
        current = ""

        def flush():
            nonlocal current
            if current.strip():
                chunks.append(current.strip())
            current = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # A single paragraph can itself be huge, so split it safely.
            while len(paragraph) > self.CHUNK_SIZE:
                room = self.CHUNK_SIZE - len(current)
                if room > 0:
                    current += ("\n\n" if current else "") + paragraph[:room]
                    flush()
                    paragraph = paragraph[room:]
                else:
                    flush()

            candidate = (
                paragraph
                if not current
                else current + "\n\n" + paragraph
            )

            if len(candidate) <= self.CHUNK_SIZE:
                current = candidate
            else:
                flush()
                current = paragraph

        flush()

        # Small overlap helps preserve concepts split at boundaries.
        if len(chunks) > 1 and self.CHUNK_OVERLAP > 0:
            overlapped = []
            for index, chunk in enumerate(chunks):
                if index == 0:
                    overlapped.append(chunk)
                    continue
                previous = chunks[index - 1]
                overlap = previous[-self.CHUNK_OVERLAP:]
                overlapped.append(overlap + "\n\n" + chunk)
            chunks = overlapped

        return chunks

    def _call(self, prompt: str, provider: str | None = None):
        return self.router.generate(
            prompt=prompt,
            preferred_provider=provider,
        )

    @staticmethod
    def _merge_meta(results: list[dict]) -> dict:
        providers = []
        errors = []
        attempts = 0
        failover = False

        for result in results:
            provider = result.get("provider")
            if provider and provider not in providers:
                providers.append(provider)
            attempts += int(result.get("attempts", 1) or 1)
            failover = failover or bool(result.get("failover", False))
            errors.extend(result.get("errors", []) or [])

        return {
            "provider": providers[0] if len(providers) == 1 else (
                "multiple" if providers else None
            ),
            "providers": providers,
            "model": results[-1].get("model") if results else None,
            "failover": failover or len(providers) > 1,
            "attempts": attempts,
            "errors": errors,
        }

    def _successful_parts(self, results: list[dict]) -> list[str]:
        parts = []
        for result in results:
            if not result.get("success"):
                continue
            response = str(result.get("response") or "").strip()
            if response:
                parts.append(response)
        return parts

    def _reduce_text(self, parts: list[str], content_type: str,
                     difficulty: str, provider: str | None) -> dict:
        """Hierarchically merge partial results so even huge PDFs remain bounded."""
        if not parts:
            return {
                "success": False,
                "provider": None,
                "model": None,
                "response": None,
                "errors": [{"provider": None, "error": "No AI result was produced."}],
            }

        current = parts[:]
        all_results: list[dict] = []

        while len(current) > 1:
            groups = []
            buffer = ""

            for part in current:
                candidate = part if not buffer else buffer + "\n\n---\n\n" + part
                if buffer and len(candidate) > self.REDUCE_GROUP_SIZE:
                    groups.append(buffer)
                    buffer = part
                else:
                    buffer = candidate
            if buffer:
                groups.append(buffer)

            next_parts = []
            for group_index, group in enumerate(groups, start=1):
                prompt = f"""
You are StudyGen, merging sections extracted from a large study document.

Content type: {content_type}
Difficulty: {difficulty}

Combine the following partial results into one accurate section.
Use ONLY information present in the supplied text. Remove duplicated content,
keep important terminology, and preserve useful headings and structure.
Do not mention that the material was chunked.

Partial results:
{group}
"""
                result = self._call(prompt, provider)
                all_results.append(result)
                if not result.get("success"):
                    return result
                response = str(result.get("response") or "").strip()
                if response:
                    next_parts.append(response)

            current = next_parts

        final = current[0]
        meta = self._merge_meta(all_results)
        return {
            "success": True,
            **meta,
            "response": final,
        }

    def _generate_text_chunks(self, chunks: list[str], content_type: str,
                              difficulty: str, provider: str | None) -> dict:
        results = []

        instructions = {
            "summary": "Create a concise revision-focused summary.",
            "notes": "Create structured academic study notes.",
            "explanation": "Explain the material clearly and logically for a student.",
        }

        for index, chunk in enumerate(chunks, start=1):
            prompt = f"""
You are StudyGen, an AI study assistant processing section {index} of a larger document.

Content type:
{content_type}

Difficulty:
{difficulty}

Task:
{instructions[content_type]}

Rules:
- Use ONLY information supported by the supplied material.
- Preserve important definitions and technical terminology.
- Keep the result self-contained enough to be merged with other sections.
- Do not mention chunking or these instructions.

Study material section:
{chunk}
"""
            result = self._call(prompt, provider)
            results.append(result)

            if not result.get("success"):
                return result

        parts = self._successful_parts(results)
        if len(parts) == 1:
            meta = self._merge_meta(results)
            return {"success": True, **meta, "response": parts[0]}

        reduced = self._reduce_text(parts, content_type, difficulty, provider)
        if reduced.get("success"):
            original_meta = self._merge_meta(results)
            reduced["providers"] = list(dict.fromkeys(
                original_meta["providers"] + reduced.get("providers", [])
            ))
            reduced["provider"] = (
                reduced["providers"][0]
                if len(reduced["providers"]) == 1
                else "multiple"
            )
            reduced["attempts"] = (
                original_meta["attempts"] + reduced.get("attempts", 0)
            )
            reduced["failover"] = (
                original_meta["failover"] or reduced.get("failover", False)
            )
        return reduced

    def _generate_structured_chunks(self, chunks: list[str], content_type: str,
                                    difficulty: str, count: int,
                                    provider: str | None) -> dict:
        # Distribute the requested count across chunks so the total requested
        # count is preserved rather than multiplying it by the number of chunks.
        chunk_count = len(chunks)
        counts = [count // chunk_count] * chunk_count
        for index in range(count % chunk_count):
            counts[index] += 1
        counts = [value for value in counts if value > 0]

        results = []
        for index, chunk in enumerate(chunks, start=1):
            local_count = counts[index - 1]
            if content_type == "mcq":
                prompt = f"""
You are StudyGen's MCQ generator processing section {index} of a larger document.
Create exactly {local_count} multiple-choice questions from ONLY the supplied material.
Difficulty: {difficulty}
Return ONLY valid JSON with this structure:
{{"questions":[{{"id":1,"question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"correct_answer":"A","explanation":"..."}}]}}
Do not use Markdown. Avoid duplicates within this section.

Material:
{chunk}
"""
            elif content_type == "flashcards":
                prompt = f"""
You are StudyGen's flashcard generator processing section {index} of a larger document.
Create exactly {local_count} flashcards using ONLY the supplied material.
Difficulty: {difficulty}
Return ONLY valid JSON:
{{"flashcards":[{{"question":"...","answer":"..."}}]}}
Do not use Markdown.

Material:
{chunk}
"""
            else:
                prompt = f"""
You are StudyGen's quiz generator processing section {index} of a larger document.
Create exactly {local_count} quiz questions using ONLY the supplied material.
Difficulty: {difficulty}
Return ONLY valid JSON:
{{"questions":[{{"id":1,"question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"correct_answer":"A","explanation":"..."}}]}}
Do not use Markdown.

Material:
{chunk}
"""

            result = self._call(prompt, provider)
            results.append(result)
            if not result.get("success"):
                return result

        meta = self._merge_meta(results)
        combined_questions = []
        combined_cards = []

        for result in results:
            raw = str(result.get("response") or "").strip()
            try:
                raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I)
                data = json.loads(raw)
            except Exception as error:
                return {
                    "success": False,
                    **meta,
                    "response": None,
                    "errors": meta["errors"] + [
                        {"provider": result.get("provider"), "error": f"Structured PDF result was not valid JSON: {error}"}
                    ],
                }

            if content_type in {"mcq", "quiz"}:
                combined_questions.extend(data.get("questions", []))
            else:
                combined_cards.extend(data.get("flashcards", []))

        if content_type in {"mcq", "quiz"}:
            for index, question in enumerate(combined_questions[:count], start=1):
                question["id"] = index
            payload = {"questions": combined_questions[:count]}
        else:
            for index, card in enumerate(combined_cards[:count], start=1):
                card["id"] = index
            payload = {"flashcards": combined_cards[:count]}

        return {
            "success": True,
            **meta,
            "response": json.dumps(payload, ensure_ascii=False),
            "data": payload,
        }

    def generate_from_material(
        self,
        material: str,
        content_type: str,
        difficulty: str = "medium",
        count: int = 5,
        provider: str | None = None,
    ) -> dict:
        material = material.strip()
        if not material:
            raise ValueError("Study material cannot be empty.")

        content_type = content_type.lower().strip()
        difficulty = difficulty.lower().strip()

        allowed = {"summary", "notes", "mcq", "flashcards", "quiz", "explanation"}
        if content_type not in allowed:
            raise ValueError(
                "Unsupported content type. Use: explanation, summary, notes, mcq, flashcards, or quiz."
            )

        if count < 1 or count > 50:
            raise ValueError("Count must be between 1 and 50.")

        chunks = self._split_material(material)
        if not chunks:
            raise ValueError("Study material could not be split into readable sections.")

        if content_type in {"mcq", "flashcards", "quiz"}:
            return self._generate_structured_chunks(
                chunks, content_type, difficulty, count, provider
            )

        return self._generate_text_chunks(
            chunks, content_type, difficulty, provider
        )
