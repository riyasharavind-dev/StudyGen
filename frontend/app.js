
const API_BASE = "https://studygen-backend-wo68.onrender.com";

const state = {
    providers: [],
    pdfFile: null,
    busy: false,

    quiz: {
        id: null,
        questions: [],
        answers: {},
        current: 0,
        locked: {},
        feedback: {},
        submitted: false,
    },
};

/* =========================================================
   DOM
========================================================= */

const $ = (id) =>
    document.getElementById(id);

const qsa = (selector) =>
    document.querySelectorAll(selector);


/* =========================================================
   INIT
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {
        initializeChat();
        initializePDFUpload();
        initializeProviders();
        initializePromptCards();
        checkBackend();
    }
);


/* =========================================================
   CHAT UI
========================================================= */

function initializeChat() {
    const input = $("chatInput");
    const send = $("sendButton");

    send?.addEventListener(
        "click",
        sendChat
    );

    input?.addEventListener(
        "keydown",
        (event) => {
            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();
                sendChat();
            }
        }
    );

    input?.addEventListener(
        "input",
        autoResizeInput
    );

    $("newChatButton")?.addEventListener(
        "click",
        startNewChat
    );

    $("contentType")?.addEventListener(
        "change",
        updateComposerControls
    );

    updateComposerControls();
}

function autoResizeInput() {
    const input = $("chatInput");

    if (!input) {
        return;
    }

    input.style.height = "auto";
    input.style.height =
        Math.min(
            input.scrollHeight,
            170
        ) + "px";
}

function updateComposerControls() {
    const type =
        $("contentType")?.value;

    const count =
        $("questionCount");

    if (!count) {
        return;
    }

    const countNeeded = [
        "mcq",
        "flashcards",
        "quiz",
    ].includes(type);

    count.style.display =
        countNeeded
            ? ""
            : "none";
}

function initializePromptCards() {
    qsa(".prompt-card").forEach(
        (button) => {
            button.addEventListener(
                "click",
                () => {
                    if (
                        button.dataset.action ===
                        "pdf"
                    ) {
                        $("pdfInput")?.click();
                        return;
                    }

                    const prompt =
                        button.dataset.prompt || "";

                    $("chatInput").value =
                        prompt;

                    autoResizeInput();
                    $("chatInput").focus();
                }
            );
        }
    );
}

function startNewChat() {
    $("chatMessages").innerHTML = "";
    $("welcomeScreen").classList.remove("hidden");

    state.quiz = {
        id: null,
        questions: [],
        answers: {},
        current: 0,
        locked: {},
        feedback: {},
        submitted: false,
    };

    removePDF();

    $("chatInput").value = "";
    autoResizeInput();
    $("chatInput").focus();
}

function appendUserMessage(text, file = null) {
    const container =
        $("chatMessages");

    const wrapper =
        document.createElement("article");

    wrapper.className =
        "chat-message user";

    const body =
        document.createElement("div");

    body.className =
        "message-body";

    const label =
        document.createElement("div");

    label.className =
        "message-label";

    label.textContent =
        "You";

    const bubble =
        document.createElement("div");

    bubble.className =
        "user-bubble";

    bubble.textContent =
        text ||
        (
            file
                ? "Please study this PDF."
                : ""
        );

    body.appendChild(label);
    body.appendChild(bubble);

    if (file) {
        const attachment =
            document.createElement("div");

        attachment.className =
            "attachment-preview";

        attachment.innerHTML = `
            <div class="attachment-icon">PDF</div>
            <div class="attachment-info">
                <strong>${escapeHTML(file.name)}</strong>
                <span>${formatFileSize(file.size)}</span>
            </div>
        `;

        body.appendChild(attachment);
    }

    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "R";

    wrapper.appendChild(body);
    wrapper.appendChild(avatar);

    container.appendChild(wrapper);

    scrollChat();
}

function appendAssistantMessage(contentHTML) {
    const container =
        $("chatMessages");

    const wrapper =
        document.createElement("article");

    wrapper.className =
        "chat-message assistant";

    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "S";

    const body =
        document.createElement("div");

    body.className =
        "message-body";

    const label =
        document.createElement("div");

    label.className =
        "message-label";

    label.textContent =
        "StudyGen";

    const content =
        document.createElement("div");

    content.className =
        "assistant-content";

    content.innerHTML =
        contentHTML;

    body.appendChild(label);
    body.appendChild(content);

    wrapper.appendChild(avatar);
    wrapper.appendChild(body);

    container.appendChild(wrapper);

    $("welcomeScreen")
        .classList.add("hidden");

    scrollChat();

    return content;
}

function scrollChat() {
    const main =
        $("chatMain");

    requestAnimationFrame(
        () => {
            main.scrollTop =
                main.scrollHeight;
        }
    );
}


/* =========================================================
   SEND / GENERATE
========================================================= */

async function sendChat() {
    if (state.busy) {
        return;
    }

    const input =
        $("chatInput");

    const text =
        input?.value.trim() || "";

    const file =
        state.pdfFile;

    if (!text && !file) {
        input?.focus();
        return;
    }

    const type =
        $("contentType")?.value ||
        "explanation";

    const difficulty =
        $("difficulty")?.value ||
        "medium";

    const count =
        Number(
            $("questionCount")?.value ||
            5
        );

    const provider =
        $("providerSelect")?.value ||
        null;

    appendUserMessage(
        text ||
        "Study this PDF and create useful learning content.",
        file
    );

    input.value = "";
    autoResizeInput();

    setBusy(
        true,
        file
            ? "Reading your PDF..."
            : "Thinking..."
    );

    try {
        if (file) {
            await generateFromPDF(
                file,
                type,
                difficulty,
                count,
                provider
            );

            removePDF();
            return;
        }

        if (type === "quiz") {
            await createInteractiveQuiz(
                text,
                difficulty,
                count,
                provider
            );

            return;
        }

        const data =
            await postJSON(
                "/study/generate",
                {
                    topic: text,
                    content_type: type,
                    difficulty,
                    count,
                    provider,
                }
            );

        renderStudyResponseToChat(
            data
        );

    } catch (error) {
        appendAssistantMessage(
            renderErrorHTML(
                error.message
            )
        );
    } finally {
        setBusy(false);
    }
}


/* =========================================================
   STUDY GENERATION
========================================================= */

function renderStudyResponseToChat(
    data
) {
    const type =
        String(
            data.type || ""
        ).toLowerCase();

    if (
        type === "quiz"
    ) {
        renderGeneratedQuestions(
            data.data
        );
        return;
    }

    if (
        type === "mcq"
    ) {
        renderGeneratedQuestions(
            data.data
        );
        return;
    }

    if (
        type === "flashcards"
    ) {
        appendAssistantMessage(
            renderFlashcards(
                data.data
            )
        );
        return;
    }

    const content =
        data.content ||
        data.response ||
        "";

    appendAssistantMessage(
        renderStudyText(
            content
        )
    );
}

function renderGeneratedQuestions(
    data
) {
    const questions =
        extractQuestions(data);

    if (!questions.length) {
        appendAssistantMessage(
            renderStudyText(
                JSON.stringify(
                    data,
                    null,
                    2
                )
            )
        );
        return;
    }

    const html =
        questions
            .map(
                (question, index) =>
                    renderQuestionCard(
                        question,
                        index,
                        `generated-${Date.now()}-${index}`
                    )
            )
            .join("");

    appendAssistantMessage(
        `<div>${html}</div>`
    );
}

function renderFlashcards(
    data
) {
    const cards =
        Array.isArray(data)
            ? data
            : (
                data?.flashcards ||
                data?.cards ||
                []
            );

    if (!cards.length) {
        return renderStudyText(
            JSON.stringify(
                data,
                null,
                2
            )
        );
    }

    return cards
        .map(
            (card, index) => {
                const front =
                    card.question ||
                    card.front ||
                    card.term ||
                    "";

                const back =
                    card.answer ||
                    card.back ||
                    card.definition ||
                    "";

                return `
                    <section class="study-section">
                        <h3>Card ${index + 1}</h3>
                        <p><strong>Question</strong></p>
                        <p>${escapeHTML(front)}</p>
                        <p><strong>Answer</strong></p>
                        <p>${escapeHTML(back)}</p>
                    </section>
                `;
            }
        )
        .join("");
}


/* =========================================================
   INTERACTIVE QUIZ
========================================================= */

async function createInteractiveQuiz(
    topic,
    difficulty,
    count,
    provider
) {
    const data =
        await postJSON(
            "/quiz/create",
            {
                topic,
                difficulty,
                count,
                provider,
            }
        );

    if (
        !data.quiz_id ||
        !Array.isArray(data.questions) ||
        !data.questions.length
    ) {
        throw new Error(
            "The backend returned an invalid quiz."
        );
    }

    state.quiz = {
        id: data.quiz_id,
        questions: data.questions,
        answers: {},
        current: 0,
        locked: {},
        feedback: {},
        submitted: false,
    };

    renderInteractiveQuiz();
}

function renderInteractiveQuiz() {
    const quiz =
        state.quiz;

    const html =
        quiz.questions
            .map(
                (question, index) =>
                    renderQuestionCard(
                        question,
                        index,
                        `quiz-${index}`
                    )
            )
            .join("");

    appendAssistantMessage(
        `
        <div class="quiz-intro-section study-section">
            <h2>Interactive Quiz</h2>
            <p>Select an answer. Correct answers turn <strong>green</strong>; wrong answers turn <strong>red</strong>.</p>
        </div>
        <div class="interactive-quiz" data-quiz="true">
            ${html}
            <div class="quiz-submit-row">
                <button
                    class="quiz-submit-button"
                    data-submit-quiz="true"
                >
                    Submit Quiz
                </button>
            </div>
        </div>
        `
    );

    bindQuizButtons();
}

function renderQuestionCard(
    question,
    index,
    keyPrefix
) {
    const options =
        normalizeOptions(
            question.options
        );

    if (!options.length) {
        return `
            <section class="study-section">
                <h3>Question ${index + 1}</h3>
                <p>${escapeHTML(
                    question.question || ""
                )}</p>
            </section>
        `;
    }

    const feedback =
        getQuestionFeedback(
            question,
            index
        );

    const correctKey =
        getCorrectAnswer(
            question
        );

    const selectedKey =
        feedback?.selected ||
        null;

    return `
        <section
            class="quiz-card"
            data-question-index="${index}"
            data-quiz-prefix="${escapeAttribute(keyPrefix)}"
        >
            <div class="quiz-card-header">
                <span class="quiz-number">
                    Question ${index + 1}
                </span>
                <span class="quiz-status">
                    ${feedback?.locked ? "Answered" : "Choose one"}
                </span>
            </div>

            <div class="quiz-question">
                ${escapeHTML(
                    question.question || ""
                )}
            </div>

            <div class="quiz-options">
                ${options
                    .map(
                        ([key, value]) => {
                            let cls =
                                "quiz-option";

                            if (
                                feedback?.locked &&
                                key === selectedKey &&
                                feedback.correct === true
                            ) {
                                cls += " correct";
                            }

                            if (
                                feedback?.locked &&
                                key === selectedKey &&
                                feedback.correct === false
                            ) {
                                cls += " wrong";
                            }

                            if (
                                feedback?.locked &&
                                feedback.correct === false &&
                                correctKey &&
                                key === correctKey
                            ) {
                                cls += " correct";
                            }

                            const disabled =
                                feedback?.locked
                                    ? "disabled"
                                    : "";

                            return `
                                <button
                                    type="button"
                                    class="${cls}"
                                    data-quiz-option="${index}"
                                    data-key="${escapeAttribute(key)}"
                                    ${disabled}
                                >
                                    <span class="option-key">
                                        ${escapeHTML(key)}
                                    </span>
                                    <span>
                                        ${escapeHTML(value)}
                                    </span>
                                </button>
                            `;
                        }
                    )
                    .join("")}
            </div>

            ${
                feedback?.locked &&
                question.explanation
                    ? `
                    <div class="quiz-explanation">
                        ${escapeHTML(
                            question.explanation
                        )}
                    </div>
                    `
                    : ""
            }
        </section>
    `;
}

function bindQuizButtons() {
    qsa(
        "[data-quiz-option]"
    ).forEach(
        (button) => {
            button.addEventListener(
                "click",
                () => {
                    const index =
                        Number(
                            button.dataset.quizOption
                        );

                    const key =
                        button.dataset.key;

                    answerQuizQuestion(
                        index,
                        key
                    );
                }
            );
        }
    );

    qsa(
        "[data-submit-quiz]"
    ).forEach(
        (button) => {
            button.addEventListener(
                "click",
                submitInteractiveQuiz
            );
        }
    );
}

function answerQuizQuestion(
    index,
    key
) {
    const question =
        state.quiz.questions[index];

    if (!question) {
        return;
    }

    if (
        state.quiz.locked[index]
    ) {
        return;
    }

    state.quiz.answers[
        String(
            question.id ?? index
        )
    ] = key;

    const correctKey =
        getCorrectAnswer(
            question
        );

    /*
     * Immediate feedback is shown when the backend
     * includes the correct answer in the question.
     */
    if (correctKey) {
        state.quiz.feedback[index] = {
            selected: key,
            locked: true,
            correct:
                normalizeKey(key) ===
                normalizeKey(correctKey),
        };

        state.quiz.locked[index] =
            true;

        rerenderInteractiveQuiz();
        return;
    }

    /*
     * If the backend deliberately does not expose
     * the answer, keep the selected option visible.
     * The final /quiz/submit call remains authoritative.
     */
    state.quiz.feedback[index] = {
        selected: key,
        locked: false,
        correct: null,
    };

    rerenderInteractiveQuiz();
}

function rerenderInteractiveQuiz() {
    const existing =
        document.querySelector(
            ".interactive-quiz"
        );

    if (!existing) {
        return;
    }

    existing.outerHTML =
        `
        <div class="interactive-quiz" data-quiz="true">
            ${state.quiz.questions
                .map(
                    (question, index) =>
                        renderQuestionCard(
                            question,
                            index,
                            `quiz-${index}`
                        )
                )
                .join("")}

            <div class="quiz-submit-row">
                <button
                    class="quiz-submit-button"
                    data-submit-quiz="true"
                >
                    Submit Quiz
                </button>
            </div>
        </div>
        `;

    bindQuizButtons();
    scrollChat();
}

async function submitInteractiveQuiz() {
    if (state.quiz.submitted) {
        return;
    }

    const missing =
        state.quiz.questions.some(
            (question, index) =>
                state.quiz.answers[
                    String(
                        question.id ?? index
                    )
                ] === undefined
        );

    if (missing) {
        showToast(
            "Answer every question first.",
            "error"
        );
        return;
    }

    state.quiz.submitted = true;

    setBusy(
        true,
        "Checking your answers..."
    );

    try {
        const data =
            await postJSON(
                "/quiz/submit",
                {
                    quiz_id:
                        state.quiz.id,
                    answers:
                        state.quiz.answers,
                }
            );

        const total =
            Number(
                data.total ??
                data.total_questions ??
                state.quiz.questions.length
            );

        const correct =
            Number(
                data.correct ??
                data.correct_answers ??
                0
            );

        const percentage =
            Number(
                data.percentage ??
                data.score ??
                (
                    total
                        ? correct / total * 100
                        : 0
                )
            );

        appendAssistantMessage(
            `
            <div class="quiz-score-card">
                <div class="eyebrow">QUIZ COMPLETE</div>
                <div class="quiz-score">
                    ${Math.round(percentage)}%
                </div>
                <div class="quiz-score-text">
                    ${correct} correct out of ${total}
                </div>
            </div>
            `
        );

    } catch (error) {
        state.quiz.submitted = false;

        appendAssistantMessage(
            renderErrorHTML(
                error.message
            )
        );
    } finally {
        setBusy(false);
    }
}

function getQuestionFeedback(
    question,
    index
) {
    const local =
        state.quiz.feedback[index];

    if (local) {
        return local;
    }

    return null;
}

function getCorrectAnswer(
    question
) {
    if (!question) {
        return null;
    }

    return (
        question.correct_answer ??
        question.correctAnswer ??
        question.correct_option ??
        question.answer_key ??
        question.correct ??
        question.answer ??
        null
    );
}

function normalizeKey(value) {
    return String(
        value ?? ""
    )
        .trim()
        .toUpperCase()
        .replace(/[\s\-—:]+/g, "");
}


/* =========================================================
   PDF
========================================================= */

function initializePDFUpload() {
    $("attachPdfButton")?.addEventListener(
        "click",
        () => $("pdfInput")?.click()
    );

    $("pdfInput")?.addEventListener(
        "change",
        (event) => {
            const file =
                event.target.files?.[0];

            if (!file) {
                return;
            }

            if (
                file.type !==
                    "application/pdf" &&
                !file.name
                    .toLowerCase()
                    .endsWith(".pdf")
            ) {
                showToast(
                    "Please select a PDF file.",
                    "error"
                );

                event.target.value = "";
                return;
            }

            state.pdfFile = file;

            $("pdfName").textContent =
                file.name;

            $("pdfSize").textContent =
                formatFileSize(
                    file.size
                );

            $("pdfAttachment")
                .classList.remove(
                    "hidden"
                );

            $("attachmentHint")
                .textContent =
                "PDF attached";
        }
    );

    $("removePdfButton")?.addEventListener(
        "click",
        removePDF
    );
}

function removePDF() {
    state.pdfFile = null;

    if ($("pdfInput")) {
        $("pdfInput").value = "";
    }

    $("pdfAttachment")
        ?.classList.add(
            "hidden"
        );

    if ($("attachmentHint")) {
        $("attachmentHint").textContent =
            "PDF supported";
    }
}

async function generateFromPDF(
    file,
    contentType,
    difficulty,
    count,
    provider
) {
    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    formData.append(
        "content_type",
        contentType
    );

    formData.append(
        "difficulty",
        difficulty
    );

    formData.append(
        "count",
        String(count)
    );

    /*
     * Keep provider optional because the existing
     * backend's PDF flow accepts the original form.
     */
    if (provider) {
        formData.append(
            "provider",
            provider
        );
    }

    const response =
        await fetch(
            `${API_BASE}/study/from-pdf`,
            {
                method: "POST",
                body: formData,
            }
        );

    const data =
        await parseResponse(
            response
        );

    const type =
        String(
            data.type || ""
        ).toLowerCase();

    if (
        type === "quiz" ||
        type === "mcq"
    ) {
        renderGeneratedQuestions(
            data.data ||
            data.response
        );
        return;
    }

    if (
        type === "flashcards"
    ) {
        appendAssistantMessage(
            renderFlashcards(
                data.data ||
                data.response
            )
        );
        return;
    }

    appendAssistantMessage(
        renderStudyText(
            data.response ||
            data.content ||
            ""
        )
    );
}


/* =========================================================
   PROVIDERS
========================================================= */

function initializeProviders() {
    $("addProviderTopButton")
        ?.addEventListener(
            "click",
            openProviderModal
        );

    $("providerMenuButton")
        ?.addEventListener(
            "click",
            openProviderModal
        );

    $("closeProviderModal")
        ?.addEventListener(
            "click",
            closeProviderModal
        );

    $("cancelProviderButton")
        ?.addEventListener(
            "click",
            closeProviderModal
        );

    $("refreshProvidersButton")
        ?.addEventListener(
            "click",
            loadProviders
        );

    $("addProviderButton")
        ?.addEventListener(
            "click",
            addProvider
        );

    $("providerModal")
        ?.addEventListener(
            "click",
            (event) => {
                if (
                    event.target.id ===
                    "providerModal"
                ) {
                    closeProviderModal();
                }
            }
        );

    loadProviders();
}

function openProviderModal() {
    $("providerModal")
        ?.classList.remove(
            "hidden"
        );

    loadProviders();
}

function closeProviderModal() {
    $("providerModal")
        ?.classList.add(
            "hidden"
        );
}

async function loadProviders() {
    try {
        const response =
            await fetch(
                `${API_BASE}/providers`
            );

        const data =
            await parseResponse(
                response
            );

        const statuses =
            data.status || {};

        state.providers =
            Object.entries(
                statuses
            ).map(
                ([name, status]) => ({
                    name,
                    ...status,
                })
            );

        renderProviderSelect();
        renderProviderList();
        setConnection("online");

    } catch (error) {
        console.error(
            "Provider loading:",
            error
        );

        setConnection(
            "offline"
        );
    }
}

function renderProviderSelect() {
    const select =
        $("providerSelect");

    if (!select) {
        return;
    }

    const previous =
        select.value;

    select.innerHTML = `
        <option value="">
            Automatic Failover
        </option>
    `;

    state.providers
        .filter(
            provider =>
                provider.configured
        )
        .sort(
            (a, b) =>
                (
                    a.priority ?? 999
                ) -
                (
                    b.priority ?? 999
                )
        )
        .forEach(
            provider => {
                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    provider.name;

                option.textContent =
                    `${provider.name}${
                        provider.model
                            ? ` — ${provider.model}`
                            : ""
                    }`;

                select.appendChild(
                    option
                );
            }
        );

    if (
        previous &&
        [...select.options].some(
            option =>
                option.value ===
                previous
        )
    ) {
        select.value =
            previous;
    }

    updateActiveProviderLabel();
}

function updateActiveProviderLabel() {
    const selected =
        $("providerSelect")?.value;

    $("activeProviderLabel")
        .textContent =
        selected ||
        "Automatic Failover";
}

async function addProvider() {
    const name =
        $("providerNameInput")
            ?.value.trim();

    const apiKey =
        $("providerApiKeyInput")
            ?.value.trim();

    const model =
        $("providerModelInput")
            ?.value.trim();

    const baseUrl =
        $("providerBaseUrlInput")
            ?.value.trim();

    const priority =
        Number(
            $("providerPriorityInput")
                ?.value || 10
        );

    if (!name) {
        showToast(
            "Enter a provider name.",
            "error"
        );
        return;
    }

    if (!apiKey) {
        showToast(
            "Enter the API key.",
            "error"
        );
        return;
    }

    if (!model) {
        showToast(
            "Enter the model name.",
            "error"
        );
        return;
    }

    setBusy(
        true,
        "Adding AI provider..."
    );

    try {
        const data =
            await postJSON(
                "/providers",
                {
                    name,
                    api_key: apiKey,
                    model,
                    base_url:
                        baseUrl || null,
                    enabled: true,
                    priority,
                }
            );

        showToast(
            data.message ||
            "Provider added successfully.",
            "success"
        );

        clearProviderForm();
        await loadProviders();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    } finally {
        setBusy(false);
    }
}

function renderProviderList() {
    const container =
        $("providerList");

    if (!container) {
        return;
    }

    if (!state.providers.length) {
        container.innerHTML = `
            <div class="provider-item">
                <div class="provider-item-info">
                    <strong>No providers configured</strong>
                    <span>Add one above to use it from the chat.</span>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML =
        state.providers
            .map(
                provider => {
                    const ready =
                        provider.enabled &&
                        provider.available;

                    return `
                        <div class="provider-item">
                            <div class="provider-item-logo">
                                ${escapeHTML(
                                    provider.name
                                        .slice(0, 2)
                                )}
                            </div>

                            <div class="provider-item-info">
                                <strong>
                                    ${escapeHTML(
                                        provider.name
                                    )}
                                </strong>

                                <span>
                                    ${
                                        provider.configured
                                            ? "Configured"
                                            : "Not configured"
                                    }
                                    ·
                                    ${
                                        provider.enabled
                                            ? "Enabled"
                                            : "Disabled"
                                    }
                                    ·
                                    ${
                                        ready
                                            ? "Ready"
                                            : "Offline"
                                    }
                                </span>
                            </div>

                            <div class="provider-item-actions">
                                ${
                                    ready
                                        ? `
                                            <button
                                                class="provider-action"
                                                onclick="testProvider('${escapeAttribute(provider.name)}')"
                                            >
                                                Test
                                            </button>
                                        `
                                        : ""
                                }

                                <button
                                    class="provider-action"
                                    onclick="toggleProvider(
                                        '${escapeAttribute(provider.name)}',
                                        ${!provider.enabled}
                                    )"
                                >
                                    ${
                                        provider.enabled
                                            ? "Disable"
                                            : "Enable"
                                    }
                                </button>

                                ${
                                    provider.configured
                                        ? `
                                            <button
                                                class="provider-action danger"
                                                onclick="removeProvider('${escapeAttribute(provider.name)}')"
                                            >
                                                Remove
                                            </button>
                                        `
                                        : ""
                                }
                            </div>
                        </div>
                    `;
                }
            )
            .join("");
}

function clearProviderForm() {
    [
        "providerNameInput",
        "providerApiKeyInput",
        "providerModelInput",
        "providerBaseUrlInput",
    ].forEach(
        id => {
            const el = $(id);
            if (el) {
                el.value = "";
            }
        }
    );

    if ($("providerPriorityInput")) {
        $("providerPriorityInput").value =
            10;
    }
}

async function toggleProvider(
    providerName,
    enabled
) {
    try {
        const action =
            enabled
                ? "enable"
                : "disable";

        await fetch(
            `${API_BASE}/providers/${encodeURIComponent(
                providerName
            )}/${action}`,
            {
                method: "PATCH",
            }
        );

        showToast(
            `${providerName} ${
                enabled
                    ? "enabled"
                    : "disabled"
            }.`,
            "success"
        );

        await loadProviders();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}

async function testProvider(
    providerName
) {
    setBusy(
        true,
        `Testing ${providerName}...`
    );

    try {
        const response =
            await fetch(
                `${API_BASE}/providers/${encodeURIComponent(
                    providerName
                )}/test`,
                {
                    method: "POST",
                }
            );

        const data =
            await parseResponse(
                response
            );

        if (data.success) {
            showToast(
                `${providerName} is working.`,
                "success"
            );
        } else {
            showToast(
                `${providerName} test failed.`,
                "error"
            );
        }

        await loadProviders();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    } finally {
        setBusy(false);
    }
}

async function removeProvider(
    providerName
) {
    if (
        !window.confirm(
            `Remove "${providerName}" from StudyGen?`
        )
    ) {
        return;
    }

    try {
        const response =
            await fetch(
                `${API_BASE}/providers/${encodeURIComponent(
                    providerName
                )}`,
                {
                    method: "DELETE",
                }
            );

        await parseResponse(
            response
        );

        showToast(
            `${providerName} removed.`,
            "success"
        );

        await loadProviders();

    } catch (error) {
        showToast(
            error.message,
            "error"
        );
    }
}


/* =========================================================
   CONNECTION
========================================================= */

async function checkBackend() {
    setConnection(
        "connecting"
    );

    try {
        const response =
            await fetch(
                `${API_BASE}/health`
            );

        const data =
            await parseResponse(
                response
            );

        setConnection(
            data.success
                ? "online"
                : "offline"
        );

    } catch (error) {
        setConnection(
            "offline"
        );
    }
}

function setConnection(
    status
) {
    const text =
        $("connectionText");

    const dot =
        document.querySelector(
            ".header-dot"
        );

    if (status === "online") {
        if (text) {
            text.textContent =
                "Backend online";
        }

        dot?.classList.add(
            "online"
        );

        dot?.classList.remove(
            "offline"
        );

        return;
    }

    if (status === "offline") {
        if (text) {
            text.textContent =
                "Backend offline";
        }

        dot?.classList.add(
            "offline"
        );

        dot?.classList.remove(
            "online"
        );

        return;
    }

    if (text) {
        text.textContent =
            "Connecting...";
    }

    dot?.classList.remove(
        "online",
        "offline"
    );
}


/* =========================================================
   HELPERS
========================================================= */

async function postJSON(
    path,
    body
) {
    const response =
        await fetch(
            `${API_BASE}${path}`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body:
                    JSON.stringify(
                        body
                    ),
            }
        );

    return parseResponse(
        response
    );
}

async function parseResponse(
    response
) {
    let data = {};

    try {
        data =
            await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            getErrorMessage(
                data
            )
        );
    }

    return data;
}

function getErrorMessage(
    data
) {
    if (!data) {
        return "Something went wrong.";
    }

    if (
        typeof data.detail ===
        "string"
    ) {
        return data.detail;
    }

    if (
        typeof data.error ===
        "string"
    ) {
        return data.error;
    }

    if (
        typeof data.message ===
        "string"
    ) {
        return data.message;
    }

    return "StudyGen could not complete the request.";
}

function setBusy(
    busy,
    text = "Thinking..."
) {
    state.busy =
        Boolean(busy);

    const send =
        $("sendButton");

    if (send) {
        send.disabled =
            state.busy;

        send.textContent =
            state.busy
                ? "…"
                : "↑";
    }

    const overlay =
        $("loadingOverlay");

    if (!overlay) {
        return;
    }

    if (state.busy) {
        $("loadingText").textContent =
            text;

        overlay.classList.remove(
            "hidden"
        );
    } else {
        overlay.classList.add(
            "hidden"
        );
    }
}

function showToast(
    message,
    type = "success"
) {
    const container =
        $("toastContainer");

    if (!container) {
        return;
    }

    const toast =
        document.createElement(
            "div"
        );

    toast.className =
        `toast ${type}`;

    toast.textContent =
        String(message);

    container.appendChild(
        toast
    );

    setTimeout(
        () => {
            toast.remove();
        },
        3500
    );
}

function formatFileSize(
    bytes
) {
    if (!bytes) {
        return "0 B";
    }

    const units = [
        "B",
        "KB",
        "MB",
        "GB",
    ];

    let value =
        Number(bytes);

    let index = 0;

    while (
        value >= 1024 &&
        index < units.length - 1
    ) {
        value /= 1024;
        index++;
    }

    return `${
        value >= 10
            ? value.toFixed(0)
            : value.toFixed(1)
    } ${units[index]}`;
}

function escapeHTML(
    value
) {
    return String(
        value ?? ""
    )
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}

function escapeAttribute(
    value
) {
    return escapeHTML(
        value
    ).replace(
        /`/g,
        "&#096;"
    );
}


/* =========================================================
   CLEAN MARKDOWN RENDERER
========================================================= */

function renderStudyText(
    text
) {
    const normalized =
        String(
            text ?? ""
        )
            .replace(
                /\r\n/g,
                "\n"
            )
            .replace(
                /\r/g,
                "\n"
            )
            .trim();

    if (!normalized) {
        return `
            <section class="study-section">
                <p>No content was returned.</p>
            </section>
        `;
    }

    const sections =
        normalized
            .split(
                /\n\s*---+\s*\n/g
            )
            .map(
                section =>
                    section.trim()
            )
            .filter(Boolean);

    return sections
        .map(
            section =>
                `
                <section class="study-section">
                    ${formatText(
                        section
                    )}
                </section>
                `
        )
        .join("");
}

function formatText(
    text
) {
    let source =
        String(
            text ?? ""
        )
            .replace(
                /\r\n/g,
                "\n"
            )
            .replace(
                /\r/g,
                "\n"
            )
            .trim();

    const codeBlocks = [];

    source =
        source.replace(
            /```([a-zA-Z0-9_+-]*)\n?([\s\S]*?)```/g,
            (
                match,
                language,
                code
            ) => {
                const token =
                    `@@CODE_${codeBlocks.length}@@`;

                codeBlocks.push({
                    language:
                        language || "",
                    code:
                        code.trim(),
                });

                return token;
            }
        );

    const lines =
        source.split("\n");

    const output = [];

    let paragraph = [];
    let listType = null;
    let listItems = [];

    function flushParagraph() {
        if (!paragraph.length) {
            return;
        }

        const value =
            paragraph
                .join(" ")
                .trim();

        if (value) {
            output.push(
                `<p>${formatInline(
                    value
                )}</p>`
            );
        }

        paragraph = [];
    }

    function flushList() {
        if (!listItems.length) {
            return;
        }

        const tag =
            listType === "ordered"
                ? "ol"
                : "ul";

        output.push(
            `<${tag}>` +
            listItems
                .map(
                    item =>
                        `<li>${formatInline(
                            item
                        )}</li>`
                )
                .join("") +
            `</${tag}>`
        );

        listItems = [];
        listType = null;
    }

    for (
        let i = 0;
        i < lines.length;
        i++
    ) {
        const line =
            lines[i].trim();

        if (!line) {
            flushParagraph();
            flushList();
            continue;
        }

        if (
            /^@@CODE_\d+@@$/.test(
                line
            )
        ) {
            flushParagraph();
            flushList();

            const index =
                Number(
                    line.match(
                        /\d+/
                    )[0]
                );

            const code =
                codeBlocks[index];

            output.push(
                `
                <div class="study-code">
                    ${
                        code.language
                            ? `
                            <span class="study-code-label">
                                ${escapeHTML(
                                    code.language
                                )}
                            </span>
                            `
                            : ""
                    }
                    <pre><code>${escapeHTML(
                        code.code
                    )}</code></pre>
                </div>
                `
            );

            continue;
        }

        if (
            /^#{1,3}\s+/.test(
                line
            ) ||
            /^SECTION\s+\d+/i.test(
                line
            )
        ) {
            flushParagraph();
            flushList();

            const heading =
                line
                    .replace(
                        /^#{1,3}\s*/,
                        ""
                    )
                    .trim();

            const level =
                /^SECTION\s+\d+/i.test(
                    heading
                )
                    ? 2
                    : Math.min(
                        (
                            line.match(
                                /^#+/
                            ) || [""]
                        )[0].length || 2,
                        3
                    );

            output.push(
                `<h${level}>${formatInline(
                    heading
                )}</h${level}>`
            );

            continue;
        }

        if (
            /^\|.*\|$/.test(line) &&
            i + 1 < lines.length &&
            /^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$/.test(
                lines[i + 1].trim()
            )
        ) {
            flushParagraph();
            flushList();

            const rows = [
                line
            ];

            i += 2;

            while (
                i < lines.length &&
                /^\|.*\|$/.test(
                    lines[i].trim()
                )
            ) {
                rows.push(
                    lines[i].trim()
                );

                i++;
            }

            i--;

            output.push(
                renderTable(
                    rows
                )
            );

            continue;
        }

        if (
            /^[-•*]\s+/.test(
                line
            )
        ) {
            flushParagraph();

            if (
                listType &&
                listType !== "unordered"
            ) {
                flushList();
            }

            listType =
                "unordered";

            listItems.push(
                line
                    .replace(
                        /^[-•*]\s+/,
                        ""
                    )
            );

            continue;
        }

        if (
            /^\d+[\.\)]\s+/.test(
                line
            )
        ) {
            flushParagraph();

            if (
                listType &&
                listType !== "ordered"
            ) {
                flushList();
            }

            listType =
                "ordered";

            listItems.push(
                line.replace(
                    /^\d+[\.\)]\s+/,
                    ""
                )
            );

            continue;
        }

        paragraph.push(
            line
        );
    }

    flushParagraph();
    flushList();

    return output.join("");
}

function formatInline(
    text
) {
    let value =
        escapeHTML(
            text
        );

    value =
        value.replace(
            /\*\*(.+?)\*\*/g,
            "<strong>$1</strong>"
        );

    value =
        value.replace(
            /(^|[^\w])\*([^*\n]+)\*(?=[^\w]|$)/g,
            "$1<em>$2</em>"
        );

    value =
        value.replace(
            /(^|[^\w])_([^_\n]+)_(?=[^\w]|$)/g,
            "$1<em>$2</em>"
        );

    value =
        value.replace(
            /`([^`]+)`/g,
            "<code>$1</code>"
        );

    /*
     * Remove standalone markdown stars that
     * remain after formatting.
     */
    value =
        value.replace(
            /(^|\s)\*+(?=\s|$)/g,
            "$1"
        );

    return value;
}

function renderTable(
    rows
) {
    const parse =
        row =>
            row
                .replace(
                    /^\s*\|/,
                    ""
                )
                .replace(
                    /\|\s*$/,
                    ""
                )
                .split("|")
                .map(
                    cell =>
                        cell.trim()
                );

    const header =
        parse(rows[0]);

    const body =
        rows
            .slice(1)
            .map(parse);

    return `
        <div class="study-table-wrap">
            <table class="study-table">
                <thead>
                    <tr>
                        ${header
                            .map(
                                cell =>
                                    `<th>${formatInline(
                                        cell
                                    )}</th>`
                            )
                            .join("")}
                    </tr>
                </thead>

                <tbody>
                    ${body
                        .map(
                            row =>
                                `
                                <tr>
                                    ${header
                                        .map(
                                            (_, index) =>
                                                `<td>${formatInline(
                                                    row[index] || ""
                                                )}</td>`
                                        )
                                        .join("")}
                                </tr>
                                `
                        )
                        .join("")}
                </tbody>
            </table>
        </div>
    `;
}

function extractQuestions(
    data
) {
    if (
        Array.isArray(data)
    ) {
        return data;
    }

    if (
        Array.isArray(
            data?.questions
        )
    ) {
        return data.questions;
    }

    if (
        Array.isArray(
            data?.mcqs
        )
    ) {
        return data.mcqs;
    }

    return [];
}

function normalizeOptions(
    options
) {
    if (
        !options ||
        typeof options !==
            "object"
    ) {
        return [];
    }

    if (
        Array.isArray(options)
    ) {
        return options
            .map(
                (item, index) => [
                    String.fromCharCode(
                        65 + index
                    ),
                    item
                ]
            );
    }

    return Object.entries(
        options
    );
}

function renderErrorHTML(
    message
) {
    return `
        <section class="study-section">
            <h3>Something went wrong</h3>
            <p>${escapeHTML(
                message
            )}</p>
        </section>
    `;
}
