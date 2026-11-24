from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import sys
import os

# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(PROJECT_ROOT))

from coordinator.decision_coordinator import DecisionCoordinator
from explainability.xai_explainer import XAIExplainer


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Emergency Triage AI",
    description="Multi-Agent AI-Based Adaptive Emergency Triage System",
    version="1.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# PATIENT DATA
# =========================================================

class PatientData(BaseModel):

    # Patient information
    name: str
    age: int
    mobile: str

    # Clinical information
    temperature: float
    heartrate: float
    resprate: float
    o2sat: float
    sbp: float
    dbp: float
    pain_numeric: float
    chiefcomplaint: str


# =========================================================
# ANALYZE PATIENT
# =========================================================

@app.post("/analyze")
def analyze_patient(patient: PatientData):

    # Convert Pydantic model to dictionary
    patient_data = patient.model_dump()

    # Add pain field required by existing agents
    patient_data["pain"] = str(
        patient_data["pain_numeric"]
    )

    # =====================================================
    # DECISION COORDINATOR
    # =====================================================

    coordinator = DecisionCoordinator()

    result = coordinator.analyze_patient(
        patient_data
    )

    # =====================================================
    # XAI EXPLANATION
    # =====================================================

    explainer = XAIExplainer()

    explanation = explainer.generate_explanation(
        result
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "patient": {
            "name": patient_data["name"],
            "age": patient_data["age"],
            "mobile": patient_data["mobile"]
        },

        "final_priority":
            result["final_priority"],

        "initial_priority":
            result.get(
                "initial_priority",
                result["final_priority"]
            ),

        "coordinator_confidence":
            result["confidence"],

        "safety_override":
            result.get(
                "safety_override",
                False
            ),

        "override_reasons":
            result.get(
                "override_reasons",
                []
            ),

        "ml_prediction":
            result["ml_model"]["priority"],

        "ml_confidence":
            result["ml_model"]["confidence"],

        "agent_assessments": {

            "vital_signs":
                result["vital_agent"]["assessment"],

            "symptoms":
                result["symptom_agent"]["assessment"],

            "risk":
                result["risk_agent"]["assessment"],

            "resources":
                result["resource_agent"]["assessment"]
        },

        "findings":
            result["findings"],

        "resource_findings":
            result.get(
                "resource_findings",
                []
            ),

        "scores":
            result.get(
                "scores",
                {}
            ),

        "explanation":
            explanation
    }


# =========================================================
# SERVE FRONTEND
# =========================================================

FRONTEND_DIR = PROJECT_ROOT / "frontend"

if FRONTEND_DIR.exists():

    app.mount(
        "/",
        StaticFiles(
            directory=str(FRONTEND_DIR),
            html=True
        ),
        name="frontend"
    )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn
    import webbrowser
    import threading

    URL = "http://127.0.0.1:8000/"

    print("\n")
    print("==========================================")
    print("       EMERGENCY TRIAGE AI")
    print("==========================================")
    print("")
    print(f"  Frontend : {URL}")
    print("  API Docs : http://127.0.0.1:8000/docs")
    print("")
    print("==========================================")
    print("       Server starting...")
    print("==========================================")
    print("")

    # Open the dashboard automatically in Chrome
    def open_chrome():
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            )
        ]

        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                webbrowser.register(
                    "chrome",
                    None,
                    webbrowser.BackgroundBrowser(chrome_path)
                )
                webbrowser.get("chrome").open(URL)
                return

        # Chrome not found - use default browser
        webbrowser.open(URL)

    # Wait briefly for the server to start
    threading.Timer(2.0, open_chrome).start()

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )