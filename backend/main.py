from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from ai_router import AIRouter
from study_generator import StudyGenerator
from study_material import StudyMaterialProcessor
from pdf_processor import PDFProcessor
from response_parser import AIResponseParser
from quiz_engine import QuizEngine
from quiz_store import QuizStore


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="StudyGen Universal AI API",
    description=(
        "Universal multi-provider AI backend "
        "with automatic provider failover, "
        "study generation, material processing, "
        "PDF-based study generation, "
        "and secure quiz generation."
    ),
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# AI SERVICES
# =========================================================

router = AIRouter()

study_generator = StudyGenerator(router)

study_material_processor = StudyMaterialProcessor(router)

pdf_processor = PDFProcessor()

response_parser = AIResponseParser()

quiz_engine = QuizEngine()

quiz_store = QuizStore()


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_CONTENT_TYPES = {
    "explanation",
    "summary",
    "notes",
    "mcq",
    "flashcards",
    "quiz",
}

ALLOWED_DIFFICULTIES = {
    "easy",
    "medium",
    "hard",
}


# =========================================================
# REQUEST MODELS
# =========================================================

class GenerateRequest(BaseModel):

    prompt: str = Field(
        ...,
        min_length=1,
        description="Prompt to send to the AI.",
    )

    provider: str | None = Field(
        default=None,
        description="Optional preferred provider.",
    )

    model: str | None = Field(
        default=None,
        description="Optional model override.",
    )


# =========================================================
# PROVIDER MODEL
# =========================================================

class AddProviderRequest(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        description="Provider name.",
    )

    api_key: str = Field(
        ...,
        min_length=1,
        description="Provider API key.",
    )

    model: str = Field(
        ...,
        min_length=1,
        description="Default model.",
    )

    base_url: str | None = Field(
        default=None,
        description="Optional custom API base URL.",
    )

    enabled: bool = Field(
        default=True,
        description="Whether the provider is enabled.",
    )

    priority: int = Field(
        default=10,
        ge=1,
        description=(
            "Provider priority. "
            "Lower number means higher priority."
        ),
    )


# =========================================================
# STUDY GENERATION MODEL
# =========================================================

class StudyGenerateRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=1,
        description="Study topic.",
    )

    content_type: str = Field(
        ...,
        min_length=1,
        description=(
            "explanation, summary, notes, "
            "mcq, flashcards, or quiz."
        ),
    )

    difficulty: str = Field(
        default="medium",
        description=(
            "Difficulty level: easy, medium, or hard."
        ),
    )

    count: int = Field(
        default=5,
        ge=1,
        le=50,
        description=(
            "Number of questions/cards when applicable."
        ),
    )

    provider: str | None = Field(
        default=None,
        description="Optional preferred AI provider.",
    )


# =========================================================
# MATERIAL GENERATION MODEL
# =========================================================

class MaterialGenerateRequest(BaseModel):

    material: str = Field(
        ...,
        min_length=1,
        description="Study material or notes.",
    )

    content_type: str = Field(
        ...,
        min_length=1,
        description=(
            "explanation, summary, notes, "
            "mcq, flashcards, or quiz."
        ),
    )

    difficulty: str = Field(
        default="medium",
        description=(
            "Difficulty level: easy, medium, or hard."
        ),
    )

    count: int = Field(
        default=5,
        ge=1,
        le=50,
        description=(
            "Number of questions/cards when applicable."
        ),
    )

    provider: str | None = Field(
        default=None,
        description="Optional preferred AI provider.",
    )


# =========================================================
# NOTES MODEL
# =========================================================

class NotesGenerateRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=1,
        description="Topic for generating study notes.",
    )

    level: str = Field(
        default="college",
        min_length=1,
        description="Academic level.",
    )

    provider: str | None = Field(
        default=None,
        description="Optional preferred provider.",
    )

    model: str | None = Field(
        default=None,
        description="Optional model override.",
    )


# =========================================================
# SECURE QUIZ MODELS
# =========================================================

class QuizCreateRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=1,
        description="Quiz topic.",
    )

    difficulty: str = Field(
        default="medium",
        description="Quiz difficulty.",
    )

    count: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of questions.",
    )

    provider: str | None = Field(
        default=None,
        description="Optional preferred provider.",
    )


class SecureQuizSubmitRequest(BaseModel):

    quiz_id: str = Field(
        ...,
        min_length=1,
        description="Secure quiz ID.",
    )

    answers: dict[str, str] = Field(
        ...,
        description=(
            "Mapping of question IDs to selected answers."
        ),
    )


# =========================================================
# OPTIONAL DIRECT QUIZ MODELS
# =========================================================

class QuizQuestion(BaseModel):

    id: int

    question: str

    options: dict[str, str]

    correct_answer: str

    explanation: str = ""


class QuizSubmitRequest(BaseModel):

    questions: list[QuizQuestion] = Field(
        ...,
        min_length=1,
    )

    answers: dict[str, str]


# =========================================================
# VALIDATION HELPERS
# =========================================================

def normalize_content_type(
    content_type: str,
) -> str:

    value = (
        content_type
        .strip()
        .lower()
    )

    if value not in ALLOWED_CONTENT_TYPES:

        raise ValueError(
            "Unsupported content type. "
            "Use: explanation, summary, notes, "
            "mcq, flashcards, or quiz."
        )

    return value


def normalize_difficulty(
    difficulty: str,
) -> str:

    value = (
        difficulty
        .strip()
        .lower()
    )

    if value not in ALLOWED_DIFFICULTIES:

        raise ValueError(
            "Invalid difficulty. "
            "Use: easy, medium, or hard."
        )

    return value


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "name": "StudyGen Universal AI API",
        "status": "online",
        "version": "1.0.0",
        "description": (
            "Universal multi-provider AI backend "
            "with automatic failover, "
            "study generation, material processing, "
            "PDF study generation, "
            "and secure quizzes."
        ),
    }


# =========================================================
# PROVIDERS
# =========================================================

@app.get("/providers")
def providers():

    return {
        "providers": router.manager.list_providers(),
        "status": router.status(),
    }


# =========================================================
# PROVIDER CONFIGURATION
# =========================================================

@app.get("/providers/config")
def provider_configs():

    configs = router.manager.get_configs()

    return {
        "providers": [
            {
                "name": config.name,
                "model": config.model,
                "enabled": config.enabled,
                "priority": config.priority,
                "base_url": config.base_url,
                "has_api_key": bool(
                    config.api_key
                ),
            }
            for config in configs
        ]
    }


# =========================================================
# ADD PROVIDER
# =========================================================

@app.post("/providers")
def add_provider(
    request: AddProviderRequest,
):

    try:

        config = router.manager.add_provider(
            name=request.name,
            api_key=request.api_key,
            model=request.model,
            base_url=request.base_url,
            enabled=request.enabled,
            priority=request.priority,
        )

        return {
            "success": True,
            "provider": {
                "name": config.name,
                "model": config.model,
                "enabled": config.enabled,
                "priority": config.priority,
                "base_url": config.base_url,
                "has_api_key": bool(
                    config.api_key
                ),
            },
        }

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# =========================================================
# GET SINGLE PROVIDER
# =========================================================

@app.get(
    "/providers/{provider_name}"
)
def get_provider(
    provider_name: str,
):

    name = (
        provider_name
        .strip()
        .lower()
    )

    config = router.manager.registry.get(
        name
    )

    if config is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Provider '{provider_name}' "
                "not found."
            ),
        )

    return {
        "name": config.name,
        "model": config.model,
        "enabled": config.enabled,
        "priority": config.priority,
        "base_url": config.base_url,
        "has_api_key": bool(
            config.api_key
        ),
    }


# =========================================================
# ENABLE PROVIDER
# =========================================================

@app.patch(
    "/providers/{provider_name}/enable"
)
def enable_provider(
    provider_name: str,
):

    try:

        router.manager.enable_provider(
            provider_name
        )

        return {
            "success": True,
            "provider": provider_name,
            "enabled": True,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# =========================================================
# DISABLE PROVIDER
# =========================================================

@app.patch(
    "/providers/{provider_name}/disable"
)
def disable_provider(
    provider_name: str,
):

    try:

        router.manager.disable_provider(
            provider_name
        )

        return {
            "success": True,
            "provider": provider_name,
            "enabled": False,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# =========================================================
# REMOVE PROVIDER
# =========================================================

@app.delete(
    "/providers/{provider_name}"
)
def remove_provider(
    provider_name: str,
):

    try:

        router.manager.remove_provider(
            provider_name
        )

        return {
            "success": True,
            "provider": provider_name,
            "removed": True,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# =========================================================
# TEST PROVIDER
# =========================================================

@app.post(
    "/providers/{provider_name}/test"
)
def test_provider(
    provider_name: str,
):

    try:

        provider = router.manager.get_provider(
            provider_name
        )

        result = provider.generate(
            prompt=(
                "Reply with exactly: "
                "StudyGen provider test successful."
            )
        )

        return {
            "success": True,
            "provider": provider_name,
            "model": getattr(
                provider,
                "model",
                None,
            ),
            "response": result,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        return {
            "success": False,
            "provider": provider_name,
            "error": str(error),
        }


# =========================================================
# UNIVERSAL AI GENERATION
# =========================================================

@app.post("/generate")
def generate(
    request: GenerateRequest,
):

    try:

        result = router.generate(
            prompt=request.prompt,
            preferred_provider=request.provider,
            model=request.model,
        )

        if not result.get("success"):

            raise HTTPException(
                status_code=503,
                detail=result,
            )

        return result

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# STUDY GENERATION FROM TOPIC
# =========================================================

@app.post("/study/generate")
def generate_study_content(
    request: StudyGenerateRequest,
):

    try:

        content_type = normalize_content_type(
            request.content_type
        )

        difficulty = normalize_difficulty(
            request.difficulty
        )

        result = study_generator.generate(
            topic=request.topic,
            content_type=content_type,
            difficulty=difficulty,
            count=request.count,
            provider=request.provider,
        )

        if not result.get("success"):

            raise HTTPException(
                status_code=503,
                detail=result,
            )

        response = result.get(
            "response",
            "",
        )

        base_response = {
            "success": True,
            "type": content_type,
            "topic": request.topic,
            "difficulty": difficulty,
            "count": request.count,
            "provider": result.get(
                "provider"
            ),
            "model": result.get(
                "model"
            ),
            "failover": result.get(
                "failover",
                False,
            ),
            "attempts": result.get(
                "attempts",
                1,
            ),
            "errors": result.get(
                "errors",
                [],
            ),
        }

        # -----------------------------------------------------
        # MCQ
        # -----------------------------------------------------

        if content_type == "mcq":

            parsed = response_parser.parse_json(
                response
            )

            validated = response_parser.validate_mcq(
                parsed
            )

            return {
                **base_response,
                "data": validated,
            }

        # -----------------------------------------------------
        # FLASHCARDS
        # -----------------------------------------------------

        if content_type == "flashcards":

            parsed = response_parser.parse_json(
                response
            )

            validated = (
                response_parser
                .validate_flashcards(
                    parsed
                )
            )

            return {
                **base_response,
                "data": validated,
            }

        # -----------------------------------------------------
        # QUIZ
        # -----------------------------------------------------

        if content_type == "quiz":

            parsed = response_parser.parse_json(
                response
            )

            validated = response_parser.validate_mcq(
                parsed
            )

            return {
                **base_response,
                "data": validated,
            }

        # -----------------------------------------------------
        # NORMAL TEXT
        # -----------------------------------------------------

        return {
            **base_response,
            "content": response,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# STUDY GENERATION FROM MATERIAL
# =========================================================

@app.post("/study/from-material")
def generate_from_material(
    request: MaterialGenerateRequest,
):

    try:

        content_type = normalize_content_type(
            request.content_type
        )

        difficulty = normalize_difficulty(
            request.difficulty
        )

        result = (
            study_material_processor
            .generate_from_material(
                material=request.material,
                content_type=content_type,
                difficulty=difficulty,
                count=request.count,
                provider=request.provider,
            )
        )

        if not result.get("success"):

            raise HTTPException(
                status_code=503,
                detail=result,
            )

        return {
            "success": True,
            "type": content_type,
            "difficulty": difficulty,
            "count": request.count,
            "provider": result.get(
                "provider"
            ),
            "model": result.get(
                "model"
            ),
            "failover": result.get(
                "failover",
                False,
            ),
            "attempts": result.get(
                "attempts",
                1,
            ),
            "response": result.get(
                "response",
                "",
            ),
            "errors": result.get(
                "errors",
                [],
            ),
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# PDF → STUDY GENERATION
# =========================================================

@app.post("/study/from-pdf")
async def generate_from_pdf(
    file: UploadFile = File(...),
    content_type: str = "summary",
    difficulty: str = "medium",
    count: int = 5,
    provider: str | None = None,
):

    # -----------------------------------------------------
    # Filename
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    # -----------------------------------------------------
    # Extension
    # -----------------------------------------------------

    if not file.filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # -----------------------------------------------------
    # Count
    # -----------------------------------------------------

    if count < 1 or count > 50:

        raise HTTPException(
            status_code=400,
            detail="Count must be between 1 and 50.",
        )

    # -----------------------------------------------------
    # Content type
    # -----------------------------------------------------

    try:

        content_type = normalize_content_type(
            content_type
        )

        difficulty = normalize_difficulty(
            difficulty
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    # -----------------------------------------------------
    # Process
    # -----------------------------------------------------

    try:

        # FastAPI keeps UploadFile content in a spooled temporary file.
        # Pass that file directly to the PDF processor instead of reading the
        # entire PDF into RAM. This makes large PDFs much safer to process.
        try:
            file.file.seek(0)
            first_byte = file.file.read(1)
            file.file.seek(0)
        except Exception:
            first_byte = b""

        if not first_byte:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty.",
            )

        pdf_result = pdf_processor.extract_text(file.file)

        material = pdf_result.get(
            "text",
            "",
        )

        if not material.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "No readable text was found "
                    "in the PDF."
                ),
            )

        # -------------------------------------------------
        # AI
        # -------------------------------------------------

        result = (
            study_material_processor
            .generate_from_material(
                material=material,
                content_type=content_type,
                difficulty=difficulty,
                count=count,
                provider=provider,
            )
        )

        if not result.get("success"):

            raise HTTPException(
                status_code=503,
                detail=result,
            )

        # -------------------------------------------------
        # Return
        # -------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "pages": pdf_result.get(
                "pages",
                0,
            ),
            "text_pages": pdf_result.get(
                "text_pages",
                0,
            ),
            "characters": pdf_result.get(
                "characters",
                len(material),
            ),
            "processing": {
                "mode": "chunked",
                "chunk_size": study_material_processor.CHUNK_SIZE,
                "message": "Large PDFs are automatically split into AI-sized sections before generation.",
            },
            "data": result.get("data"),
            "type": content_type,
            "difficulty": difficulty,
            "count": count,
            "provider": result.get(
                "provider"
            ),
            "model": result.get(
                "model"
            ),
            "failover": result.get(
                "failover",
                False,
            ),
            "attempts": result.get(
                "attempts",
                1,
            ),
            "response": result.get(
                "response",
                "",
            ),
            "errors": result.get(
                "errors",
                [],
            ),
        }

    except HTTPException:

        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# STUDY NOTES
# =========================================================

@app.post("/study/notes")
def generate_notes(
    request: NotesGenerateRequest,
):

    try:

        result = study_generator.generate_notes(
            topic=request.topic,
            level=request.level,
            provider=request.provider,
            model=request.model,
        )

        if not result.get("success"):

            raise HTTPException(
                status_code=503,
                detail=result,
            )

        return {
            "success": True,
            "type": "notes",
            "topic": request.topic,
            "level": request.level,
            "provider": result.get(
                "provider"
            ),
            "model": result.get(
                "model"
            ),
            "failover": result.get(
                "failover",
                False,
            ),
            "attempts": result.get(
                "attempts",
                1,
            ),
            "content": result.get(
                "response",
                "",
            ),
            "errors": result.get(
                "errors",
                [],
            ),
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# SECURE QUIZ CREATION
#
# IMPORTANT:
# Correct answers stay on the backend.
# Frontend receives only public questions.
# =========================================================

@app.post("/quiz/create")
def create_quiz(
    request: QuizCreateRequest,
):

    try:

        difficulty = normalize_difficulty(
            request.difficulty
        )

        result = study_generator.generate(
            topic=request.topic,
            content_type="quiz",
            difficulty=difficulty,
            count=request.count,
            provider=request.provider,
        )

        if not result.get("success"):

            raise HTTPException(
                status_code=503,
                detail=result,
            )

        raw_response = result.get(
            "response",
            "",
        )

        parsed = response_parser.parse_json(
            raw_response
        )

        validated = response_parser.validate_mcq(
            parsed
        )

        questions = validated.get(
            "questions",
            []
        )

        if not questions:

            raise ValueError(
                "AI returned no quiz questions."
            )

        # -------------------------------------------------
        # Store COMPLETE questions
        # -------------------------------------------------

        quiz_id = quiz_store.create(
            questions=questions,
            topic=request.topic,
            difficulty=difficulty,
        )

        # -------------------------------------------------
        # Hide correct answers
        # -------------------------------------------------

        public_questions = []

        for question in questions:

            public_questions.append(
                {
                    "id": question["id"],
                    "question": question[
                        "question"
                    ],
                    "options": question[
                        "options"
                    ],
                }
            )

        return {
            "success": True,
            "quiz_id": quiz_id,
            "topic": request.topic,
            "difficulty": difficulty,
            "count": len(
                public_questions
            ),
            "provider": result.get(
                "provider"
            ),
            "model": result.get(
                "model"
            ),
            "failover": result.get(
                "failover",
                False,
            ),
            "attempts": result.get(
                "attempts",
                1,
            ),
            "questions": public_questions,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# SECURE QUIZ SUBMISSION
#
# This is the ONLY /quiz/submit endpoint.
# =========================================================

@app.post("/quiz/submit")
def submit_secure_quiz(
    request: SecureQuizSubmitRequest,
):

    try:

        quiz = quiz_store.get(
            request.quiz_id
        )

        if quiz is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Quiz not found or expired."
                ),
            )

        questions = quiz.get(
            "questions",
            [],
        )

        if not questions:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Quiz contains no questions."
                ),
            )

        result = quiz_engine.evaluate(
            questions=questions,
            answers=request.answers,
        )

        # -------------------------------------------------
        # Delete after submission
        # -------------------------------------------------

        quiz_store.delete(
            request.quiz_id
        )

        return {
            "success": True,
            "quiz_id": request.quiz_id,
            "topic": quiz.get(
                "topic",
                "",
            ),
            "difficulty": quiz.get(
                "difficulty",
                "medium",
            ),
            **result,
        }

    except HTTPException:

        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    try:

        status = router.status()

        providers = router.manager.list_providers()

        return {
            "success": True,
            "status": "healthy",
            "providers": providers,
            "provider_status": status,
        }

    except Exception as error:

        return {
            "success": False,
            "status": "degraded",
            "error": str(error),
        }


# =========================================================
# END
# =========================================================