/* =========================================================
   EMERGENCY TRIAGE AI
   FRONTEND LOGIC + AI CLARIFICATION CHATBOT
   ========================================================= */

const API_URL = "http://127.0.0.1:8000/analyze";


// =========================================================
// GLOBAL STATE
// =========================================================

let latestAnalysis = null;


// =========================================================
// HELPER
// =========================================================

function getValue(id) {
    const element = document.getElementById(id);

    if (!element) {
        return "";
    }

    return element.value.trim();
}


function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? "—";
    }
}


function escapeHtml(text) {
    if (text === null || text === undefined) {
        return "";
    }

    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// =========================================================
// ANALYZE PATIENT
// =========================================================

async function analyzePatient() {

    const errorBox = document.getElementById("errorMessage");
    const loadingBox = document.getElementById("loading");
    const analyzeButton = document.getElementById("analyzeBtn");

    errorBox.style.display = "none";
    errorBox.textContent = "";

    // ---------------------------------------------
    // Read form
    // ---------------------------------------------

    const patient = {

        name: getValue("name"),

        age: Number(getValue("age")),

        mobile: getValue("mobile"),

        temperature: Number(getValue("temperature")),

        heartrate: Number(getValue("heartrate")),

        resprate: Number(getValue("resprate")),

        o2sat: Number(getValue("o2sat")),

        sbp: Number(getValue("sbp")),

        dbp: Number(getValue("dbp")),

        pain_numeric: Number(getValue("pain_numeric")),

        chiefcomplaint: getValue("chiefcomplaint")

    };


    // ---------------------------------------------
    // Basic validation
    // ---------------------------------------------

    const requiredFields = [
        ["name", patient.name],
        ["age", patient.age],
        ["mobile", patient.mobile],
        ["temperature", patient.temperature],
        ["heartrate", patient.heartrate],
        ["resprate", patient.resprate],
        ["o2sat", patient.o2sat],
        ["sbp", patient.sbp],
        ["dbp", patient.dbp],
        ["pain score", patient.pain_numeric],
        ["chief complaint", patient.chiefcomplaint]
    ];


    for (const [field, value] of requiredFields) {

        if (
            value === "" ||
            value === null ||
            value === undefined ||
            Number.isNaN(value)
        ) {

            showError(
                `Please enter a valid value for ${field}.`
            );

            return;
        }
    }


    if (patient.age < 0 || patient.age > 120) {

        showError(
            "Please enter a valid patient age."
        );

        return;
    }


    if (
        patient.pain_numeric < 0 ||
        patient.pain_numeric > 10
    ) {

        showError(
            "Pain score must be between 0 and 10."
        );

        return;
    }


    // ---------------------------------------------
    // UI loading
    // ---------------------------------------------

    loadingBox.style.display = "flex";

    analyzeButton.disabled = true;
    analyzeButton.style.opacity = "0.65";

    const resultSection =
        document.getElementById("resultSection");

    resultSection.style.display = "none";


    try {

        const response = await fetch(
            API_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(patient)
            }
        );


        if (!response.ok) {

            let message =
                `Server returned HTTP ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {
                    message = errorData.detail;
                }

            } catch (e) {
                // Ignore JSON parsing error
            }

            throw new Error(message);
        }


        const result = await response.json();


        // Save latest analysis
        latestAnalysis = result;


        displayResults(result);


        // Add contextual chatbot message
        addBotMessage(
            "The patient assessment is complete. You can now ask me to explain the priority, ML confidence, safety override, agent decisions, clinical findings or available resources."
        );


        // Scroll to result
        setTimeout(() => {

            resultSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 200);


    } catch (error) {

        console.error(error);

        showError(
            "Unable to connect to the Emergency Triage AI backend. Make sure FastAPI is running at http://127.0.0.1:8000."
        );

    } finally {

        loadingBox.style.display = "none";

        analyzeButton.disabled = false;
        analyzeButton.style.opacity = "1";
    }
}


// =========================================================
// DISPLAY RESULTS
// =========================================================

function displayResults(result) {

    const resultSection =
        document.getElementById("resultSection");

    resultSection.style.display = "block";


    // ---------------------------------------------
    // Patient
    // ---------------------------------------------

    setText(
        "resultPatientName",
        result.patient?.name || "—"
    );

    setText(
        "resultPatientAge",
        result.patient?.age ?? "—"
    );

    setText(
        "resultPatientMobile",
        result.patient?.mobile || "—"
    );


    // ---------------------------------------------
    // Priority
    // ---------------------------------------------

    const priority =
        String(result.final_priority || "UNKNOWN")
            .toUpperCase();

    const priorityBox =
        document.getElementById("priorityBox");

    priorityBox.classList.remove(
        "HIGH",
        "MODERATE",
        "LOW"
    );

    if (
        priority === "HIGH" ||
        priority === "MODERATE" ||
        priority === "LOW"
    ) {

        priorityBox.classList.add(priority);

    }

    setText(
        "priority",
        priority
    );


    // ---------------------------------------------
    // ML prediction
    // ---------------------------------------------

    const mlPrediction =
        result.ml_prediction || "—";

    const mlConfidence =
        Number(result.ml_confidence ?? 0);

    setText(
        "mlPrediction",
        mlPrediction
    );

    setText(
        "mlConfidence",
        Math.round(mlConfidence)
    );

    const mlBar =
        document.getElementById("mlConfidenceBar");

    if (mlBar) {
        mlBar.style.width =
            `${Math.max(0, Math.min(100, mlConfidence))}%`;
    }


    // ---------------------------------------------
    // Coordinator confidence
    // ---------------------------------------------

    const coordinatorConfidence =
        Number(
            result.coordinator_confidence ?? 0
        );

    setText(
        "coordinatorConfidence",
        `${Math.round(coordinatorConfidence)}%`
    );

    setText(
        "coordinatorConfidenceText",
        Math.round(coordinatorConfidence)
    );

    const coordinatorBar =
        document.getElementById(
            "coordinatorConfidenceBar"
        );

    if (coordinatorBar) {

        coordinatorBar.style.width =
            `${Math.max(
                0,
                Math.min(100, coordinatorConfidence)
            )}%`;
    }


    // ---------------------------------------------
    // Safety override
    // ---------------------------------------------

    const safetyOverride =
        Boolean(result.safety_override);

    const safetyStatus =
        document.getElementById(
            "safetyOverrideStatus"
        );

    const safetyText =
        document.getElementById(
            "safetyOverride"
        );

    const reasonsContainer =
        document.getElementById(
            "overrideReasons"
        );


    reasonsContainer.innerHTML = "";


    if (safetyOverride) {

        safetyStatus.textContent =
            "TRIGGERED";

        safetyStatus.style.color =
            "#dc3545";

        safetyText.textContent =
            "A safety rule detected one or more critical findings and influenced the final triage decision.";

        const reasons =
            result.override_reasons || [];

        reasons.forEach(reason => {

            const div =
                document.createElement("div");

            div.className =
                "override-reason";

            div.textContent =
                reason;

            reasonsContainer.appendChild(div);

        });

    } else {

        safetyStatus.textContent =
            "NOT TRIGGERED";

        safetyStatus.style.color =
            "#15966c";

        safetyText.textContent =
            "No critical safety override was applied.";

    }


    // ---------------------------------------------
    // Agents
    // ---------------------------------------------

    const agents =
        result.agent_assessments || {};

    setText(
        "vitalAgent",
        agents.vital_signs || "—"
    );

    setText(
        "symptomAgent",
        agents.symptoms || "—"
    );

    setText(
        "riskAgent",
        agents.risk || "—"
    );

    setText(
        "resourceAgent",
        agents.resources || "—"
    );


    // ---------------------------------------------
    // Findings
    // ---------------------------------------------

    renderFindings(
        "findings",
        result.findings,
        "No specific clinical findings were returned."
    );


    // ---------------------------------------------
    // Resources
    // ---------------------------------------------

    renderFindings(
        "resourceFindings",
        result.resource_findings,
        "No resource findings were returned."
    );


    // ---------------------------------------------
    // Explanation
    // ---------------------------------------------

    setText(
        "explanation",
        result.explanation ||
        "No explanation was returned by the XAI module."
    );
}


// =========================================================
// RENDER FINDINGS
// =========================================================

function renderFindings(
    containerId,
    findings,
    emptyMessage
) {

    const container =
        document.getElementById(containerId);

    if (!container) {
        return;
    }

    container.innerHTML = "";


    if (
        !Array.isArray(findings) ||
        findings.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-finding">
                ${escapeHtml(emptyMessage)}
            </div>
        `;

        return;
    }


    findings.forEach(item => {

        const div =
            document.createElement("div");

        div.className =
            "finding-item";

        div.innerHTML = `
            <span class="finding-icon"></span>
            <span>${escapeHtml(item)}</span>
        `;

        container.appendChild(div);

    });
}


// =========================================================
// ERROR
// =========================================================

function showError(message) {

    const errorBox =
        document.getElementById("errorMessage");

    errorBox.textContent = message;

    errorBox.style.display = "block";

    errorBox.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


// =========================================================
// RESET
// =========================================================

function resetForm() {

    const fields = [
        "name",
        "age",
        "mobile",
        "temperature",
        "heartrate",
        "resprate",
        "o2sat",
        "sbp",
        "dbp",
        "pain_numeric",
        "chiefcomplaint"
    ];


    fields.forEach(id => {

        const element =
            document.getElementById(id);

        if (element) {
            element.value = "";
        }

    });


    latestAnalysis = null;


    document.getElementById(
        "resultSection"
    ).style.display = "none";


    document.getElementById(
        "errorMessage"
    ).style.display = "none";


    document.getElementById(
        "loading"
    ).style.display = "none";


    // Reset confidence bars

    const mlBar =
        document.getElementById(
            "mlConfidenceBar"
        );

    const coordinatorBar =
        document.getElementById(
            "coordinatorConfidenceBar"
        );

    if (mlBar) {
        mlBar.style.width = "0%";
    }

    if (coordinatorBar) {
        coordinatorBar.style.width = "0%";
    }
}


// =========================================================
// PRINT REPORT
// =========================================================

function printReport() {

    if (!latestAnalysis) {

        alert(
            "Please analyze a patient before printing the report."
        );

        return;
    }

    window.print();
}


// =========================================================
// CHATBOT
// =========================================================

function toggleChat() {

    const chatWindow =
        document.getElementById("chatWindow");

    chatWindow.classList.toggle("open");


    if (
        chatWindow.classList.contains("open")
    ) {

        setTimeout(() => {

            document
                .getElementById("chatInput")
                .focus();

        }, 100);

    }
}


// =========================================================
// CHAT KEYBOARD
// =========================================================

function handleChatKey(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendChatMessage();

    }
}


// =========================================================
// QUICK CHAT
// =========================================================

function quickChat(question) {

    const input =
        document.getElementById("chatInput");

    input.value = question;

    sendChatMessage();
}


// =========================================================
// SEND CHAT MESSAGE
// =========================================================

function sendChatMessage() {

    const input =
        document.getElementById("chatInput");

    const message =
        input.value.trim();


    if (!message) {
        return;
    }


    addUserMessage(message);

    input.value = "";


    setTimeout(() => {

        const response =
            generateChatResponse(message);

        addBotMessage(response);

    }, 350);
}


// =========================================================
// ADD USER MESSAGE
// =========================================================

function addUserMessage(message) {

    const container =
        document.getElementById("chatMessages");


    const messageDiv =
        document.createElement("div");

    messageDiv.className =
        "chat-message user";


    messageDiv.innerHTML = `

        <div class="message-avatar">
            YOU
        </div>

        <div class="message-bubble">
            ${escapeHtml(message)}
        </div>

    `;


    container.appendChild(messageDiv);

    scrollChatToBottom();
}


// =========================================================
// ADD BOT MESSAGE
// =========================================================

function addBotMessage(message) {

    const container =
        document.getElementById("chatMessages");


    const messageDiv =
        document.createElement("div");

    messageDiv.className =
        "chat-message bot";


    const formatted =
        formatChatResponse(message);


    messageDiv.innerHTML = `

        <div class="message-avatar">
            AI
        </div>

        <div class="message-bubble">
            ${formatted}
        </div>

    `;


    container.appendChild(messageDiv);

    scrollChatToBottom();
}


// =========================================================
// FORMAT CHAT RESPONSE
// =========================================================

function formatChatResponse(text) {

    let safe =
        escapeHtml(text);


    safe =
        safe.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    safe =
        safe.replace(
            /\n/g,
            "<br>"
        );


    return safe;
}


// =========================================================
// SCROLL CHAT
// =========================================================

function scrollChatToBottom() {

    const container =
        document.getElementById(
            "chatMessages"
        );

    container.scrollTop =
        container.scrollHeight;
}


// =========================================================
// CHAT RESPONSE ENGINE
// =========================================================

function generateChatResponse(question) {

    const q =
        question
            .toLowerCase()
            .trim();


    // ---------------------------------------------
    // No analysis yet
    // ---------------------------------------------

    if (!latestAnalysis) {

        if (
            q.includes("hello") ||
            q.includes("hi") ||
            q.includes("hey")
        ) {

            return `
                Hello. I can help you understand the Emergency Triage AI interface.
                Analyze a patient first if you want patient-specific explanations.
            `;
        }


        if (
            q.includes("what can you do") ||
            q.includes("help")
        ) {

            return `
                I can explain the triage priority, ML prediction,
                confidence scores, safety override, multi-agent assessments,
                clinical findings and hospital resources.
            `;
        }


        return `
            No patient assessment is currently available.
            Please enter the patient information and click <strong>Analyze Patient</strong>
            first. After that, I can explain the generated result.
        `;
    }


    // ---------------------------------------------
    // Extract current data
    // ---------------------------------------------

    const priority =
        latestAnalysis.final_priority ||
        "UNKNOWN";

    const initialPriority =
        latestAnalysis.initial_priority ||
        priority;

    const mlPrediction =
        latestAnalysis.ml_prediction ||
        "UNKNOWN";

    const mlConfidence =
        latestAnalysis.ml_confidence ??
        "N/A";

    const coordinatorConfidence =
        latestAnalysis.coordinator_confidence ??
        "N/A";

    const safetyOverride =
        latestAnalysis.safety_override;

    const overrideReasons =
        latestAnalysis.override_reasons || [];

    const agents =
        latestAnalysis.agent_assessments || {};

    const findings =
        latestAnalysis.findings || [];

    const resources =
        latestAnalysis.resource_findings || [];


    // ---------------------------------------------
    // Greetings
    // ---------------------------------------------

    if (
        q === "hi" ||
        q === "hello" ||
        q === "hey" ||
        q.includes("good morning") ||
        q.includes("good evening")
    ) {

        return `
            Hello. The latest patient assessment is <strong>${escapeHtml(priority)}</strong>.
            What would you like me to clarify?
        `;
    }


    // ---------------------------------------------
    // Priority
    // ---------------------------------------------

    if (
        q.includes("why high") ||
        q.includes("why is") ||
        q.includes("why priority") ||
        q.includes("why this priority") ||
        q.includes("explain priority") ||
        q.includes("priority")
    ) {

        let response = `
            The current final triage priority is <strong>${escapeHtml(priority)}</strong>.
            The coordinator combines the assessments from the vital signs,
            symptoms, risk and resource agents with the ML model.
        `;


        if (
            initialPriority !== priority
        ) {

            response += `
                The initial coordinator priority was
                <strong>${escapeHtml(initialPriority)}</strong>,
                which was subsequently adjusted during the final decision process.
            `;
        }


        if (
            findings.length > 0
        ) {

            response += `
                Important findings include:
                ${findings.slice(0, 4).map(
                    f => escapeHtml(f)
                ).join(", ")}.
            `;
        }


        return response;
    }


    // ---------------------------------------------
    // ML
    // ---------------------------------------------

    if (
        q.includes("ml") ||
        q.includes("machine learning") ||
        q.includes("model") ||
        q.includes("prediction") ||
        q.includes("confidence")
    ) {

        return `
            The machine-learning model predicts
            <strong>${escapeHtml(mlPrediction)}</strong>
            with a confidence of approximately
            <strong>${escapeHtml(mlConfidence)}%</strong>.
            The ML prediction is one input to the overall triage decision;
            the final priority is produced by the coordinator after considering
            the other assessment components.
        `;
    }


    // ---------------------------------------------
    // Safety override
    // ---------------------------------------------

    if (
        q.includes("safety") ||
        q.includes("override") ||
        q.includes("critical")
    ) {

        if (safetyOverride) {

            let reasonText =
                "Critical safety conditions were identified.";

            if (
                overrideReasons.length > 0
            ) {

                reasonText =
                    overrideReasons
                        .map(
                            reason =>
                                escapeHtml(reason)
                        )
                        .join("; ");
            }


            return `
                The <strong>safety override was triggered</strong>.
                This means the safety rules detected critical findings that
                required additional protection in the final decision.
                Reasons include: ${reasonText}.
            `;

        }


        return `
            The safety override was <strong>not triggered</strong>
            for this assessment. The final decision therefore did not require
            an additional safety-rule override.
        `;
    }


    // ---------------------------------------------
    // Agents
    // ---------------------------------------------

    if (
        q.includes("agent") ||
        q.includes("multi agent") ||
        q.includes("vital agent") ||
        q.includes("symptom agent") ||
        q.includes("risk agent") ||
        q.includes("resource agent")
    ) {

        return `
            Four agents contributed to the assessment:
            <br><br>
            <strong>Vital Signs Agent:</strong>
            ${escapeHtml(agents.vital_signs || "N/A")}
            <br>
            <strong>Symptoms Agent:</strong>
            ${escapeHtml(agents.symptoms || "N/A")}
            <br>
            <strong>Risk Agent:</strong>
            ${escapeHtml(agents.risk || "N/A")}
            <br>
            <strong>Resource Agent:</strong>
            ${escapeHtml(agents.resources || "N/A")}
            <br><br>
            The coordinator combines these assessments to produce the final result.
        `;
    }


    // ---------------------------------------------
    // Findings
    // ---------------------------------------------

    if (
        q.includes("finding") ||
        q.includes("clinical") ||
        q.includes("problem") ||
        q.includes("condition")
    ) {

        if (
            findings.length === 0
        ) {

            return `
                No specific clinical findings were returned by the backend
                for this assessment.
            `;
        }


        return `
            The system returned these clinical findings:
            <br><br>
            ${findings
                .slice(0, 8)
                .map(
                    f => `• ${escapeHtml(f)}`
                )
                .join("<br>")}
        `;
    }


    // ---------------------------------------------
    // Resources
    // ---------------------------------------------

    if (
        q.includes("resource") ||
        q.includes("icu") ||
        q.includes("ventilator") ||
        q.includes("bed") ||
        q.includes("hospital")
    ) {

        if (
            resources.length === 0
        ) {

            return `
                No specific hospital resource findings were returned
                for this assessment.
            `;
        }


        return `
            The resource assessment returned:
            <br><br>
            ${resources
                .slice(0, 8)
                .map(
                    r => `• ${escapeHtml(r)}`
                )
                .join("<br>")}
        `;
    }


    // ---------------------------------------------
    // Coordinator
    // ---------------------------------------------

    if (
        q.includes("coordinator") ||
        q.includes("decision")
    ) {

        return `
            The coordinator acts as the decision-synthesis layer.
            It receives the individual agent assessments and ML prediction,
            evaluates their combined evidence and produces the final triage
            priority of <strong>${escapeHtml(priority)}</strong>.
            Its reported confidence is approximately
            <strong>${escapeHtml(coordinatorConfidence)}%</strong>.
        `;
    }


    // ---------------------------------------------
    // Explainability
    // ---------------------------------------------

    if (
        q.includes("explain") ||
        q.includes("reasoning") ||
        q.includes("how did")
    ) {

        const explanation =
            latestAnalysis.explanation ||
            "No explanation was returned.";

        return `
            The XAI explanation says:
            <br><br>
            ${escapeHtml(explanation)}
        `;
    }


    // ---------------------------------------------
    // Vital signs
    // ---------------------------------------------

    if (
        q.includes("vital") ||
        q.includes("oxygen") ||
        q.includes("spo2") ||
        q.includes("heart rate") ||
        q.includes("blood pressure")
    ) {

        return `
            The Vital Signs Agent assessed the patient's measurements as
            <strong>${escapeHtml(
                agents.vital_signs || "N/A"
            )}</strong>.
            The backend uses the submitted vital measurements as part of
            the overall triage assessment.
        `;
    }


    // ---------------------------------------------
    // What happened?
    // ---------------------------------------------

    if (
        q.includes("summary") ||
        q.includes("summarize") ||
        q.includes("overall") ||
        q.includes("result")
    ) {

        return `
            <strong>Current assessment summary:</strong>
            <br><br>
            Final Priority: <strong>${escapeHtml(priority)}</strong>
            <br>
            ML Prediction: <strong>${escapeHtml(mlPrediction)}</strong>
            <br>
            ML Confidence: <strong>${escapeHtml(mlConfidence)}%</strong>
            <br>
            Coordinator Confidence: <strong>${escapeHtml(coordinatorConfidence)}%</strong>
            <br>
            Safety Override:
            <strong>${safetyOverride ? "TRIGGERED" : "NOT TRIGGERED"}</strong>
        `;
    }


    // ---------------------------------------------
    // Reset / new patient
    // ---------------------------------------------

    if (
        q.includes("new patient") ||
        q.includes("reset")
    ) {

        return `
            To assess another patient, use the
            <strong>Reset</strong> button, enter the new patient information,
            and select <strong>Analyze Patient</strong>.
        `;
    }


    // ---------------------------------------------
    // Default
    // ---------------------------------------------

    return `
        I can clarify the current assessment. Try asking:
        <br><br>
        • Why is this patient high priority?
        <br>
        • What does the ML confidence mean?
        <br>
        • Explain the safety override.
        <br>
        • Explain the four agents.
        <br>
        • What are the clinical findings?
        <br>
        • What resources are available?
        <br>
        • Give me an overall summary.
    `;
}


// =========================================================
// STARTUP
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const chatWindow =
            document.getElementById(
                "chatWindow"
            );

        if (chatWindow) {
            chatWindow.classList.remove("open");
        }

    }
);