import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from models.predict import TriageModel
from agents.vital_agent import VitalSignsAgent
from agents.symptom_agent import SymptomAgent
from agents.risk_agent import RiskAssessmentAgent
from agents.resource_agent import assess_resources


class DecisionCoordinator:
    """
    Combines:
    - Vital Signs Agent
    - Symptom Agent
    - Risk Assessment Agent
    - ML Triage Model
    - Resource Availability Agent

    Resource availability provides operational information
    and does not change clinical priority.

    Safety override rules are applied after agent/ML scoring
    to prevent clearly critical presentations from being
    classified as LOW.
    """

    def __init__(self):

        self.agent_name = "Decision Coordinator Agent"

        self.vital_agent = VitalSignsAgent()
        self.symptom_agent = SymptomAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.ml_model = TriageModel()

    def analyze_patient(self, patient):

        # ==========================================
        # 1. RUN CLINICAL AGENTS
        # ==========================================

        vital_result = self.vital_agent.analyze(patient)

        symptom_result = self.symptom_agent.analyze(patient)

        risk_result = self.risk_agent.analyze(patient)


        # ==========================================
        # 2. RUN ML MODEL
        # ==========================================

        ml_result = self.ml_model.predict(patient)


        # ==========================================
        # 3. CHECK HOSPITAL RESOURCES
        # ==========================================

        resource_result = assess_resources()


        # ==========================================
        # 4. AGENT VOTING
        # ==========================================

        clinical_results = [
            vital_result,
            symptom_result,
            risk_result
        ]

        scores = {
            "HIGH": 0,
            "MODERATE": 0,
            "LOW": 0
        }


        for result in clinical_results:

            assessment = result["assessment"]

            if assessment == "HIGH":

                scores["HIGH"] += 3

            elif assessment == "MODERATE":

                scores["MODERATE"] += 2

            else:

                scores["LOW"] += 1


        # ==========================================
        # 5. ML MODEL CONTRIBUTION
        # ==========================================

        if ml_result["prediction"] == 1:

            scores["HIGH"] += 3

        else:

            scores["LOW"] += 3


        # ==========================================
        # 6. INITIAL DECISION
        # ==========================================

        initial_priority = max(
            scores,
            key=scores.get
        )


        # ==========================================
        # 7. SAFETY OVERRIDE
        # ==========================================

        safety_override = False
        override_reasons = []

        o2sat = patient.get("o2sat", 100)
        sbp = patient.get("sbp", 120)
        dbp = patient.get("dbp", 80)
        resprate = patient.get("resprate", 18)
        heartrate = patient.get("heartrate", 75)
        pain = patient.get("pain_numeric", 0)

        complaint = str(
            patient.get("chiefcomplaint", "")
        ).lower()


        # ------------------------------------------
        # Critical oxygen saturation
        # ------------------------------------------

        if o2sat < 90:

            safety_override = True

            override_reasons.append(
                "Critically low oxygen saturation"
            )


        # ------------------------------------------
        # Severe hypotension
        # ------------------------------------------

        if sbp < 80:

            safety_override = True

            override_reasons.append(
                "Severely low systolic blood pressure"
            )


        # ------------------------------------------
        # Significant respiratory distress
        # ------------------------------------------

        if resprate >= 30:

            safety_override = True

            override_reasons.append(
                "Significantly elevated respiratory rate"
            )


        # ------------------------------------------
        # Severe tachycardia
        # ------------------------------------------

        if heartrate >= 130:

            safety_override = True

            override_reasons.append(
                "Severe tachycardia"
            )


        # ------------------------------------------
        # Major emergency symptoms
        # ------------------------------------------

        emergency_symptoms = [
            "chest pain",
            "facial droop",
            "stroke",
            "respiratory arrest",
            "cardiac arrest",
            "seizure",
            "unconscious",
            "unresponsive",
            "severe bleeding",
            "head bleed",
            "intubated trauma"
        ]


        for symptom in emergency_symptoms:

            if symptom in complaint:

                # Only use the symptom itself as an
                # override when combined with another
                # concerning indicator.

                if (
                    o2sat < 92
                    or sbp < 90
                    or resprate >= 24
                    or heartrate >= 120
                    or pain >= 8
                    or symptom in [
                        "respiratory arrest",
                        "cardiac arrest",
                        "unconscious",
                        "unresponsive"
                    ]
                ):

                    safety_override = True

                    override_reasons.append(
                        f"High-risk emergency symptom: {symptom}"
                    )

                break


        # ==========================================
        # 8. APPLY OVERRIDE
        # ==========================================

        final_priority = initial_priority

        if safety_override:

            final_priority = "HIGH"


        # ==========================================
        # 9. CALCULATE CONFIDENCE
        # ==========================================

        total_score = sum(
            scores.values()
        )

        if total_score > 0:

            confidence = (
                scores[final_priority]
                / total_score
            ) * 100

        else:

            confidence = 0


        # Safety override should not falsely represent
        # the voting score as the confidence.
        #
        # Therefore, when an override occurs, confidence
        # is reported as a decision-system confidence.

        if safety_override:

            confidence = max(
                confidence,
                90.0
            )


        # ==========================================
        # 10. COMBINE CLINICAL FINDINGS
        # ==========================================

        findings = []

        for result in clinical_results:

            findings.extend(
                result.get(
                    "findings",
                    []
                )
            )


        # Remove duplicate findings

        findings = list(
            dict.fromkeys(findings)
        )


        # ==========================================
        # 11. ADD SAFETY OVERRIDE FINDINGS
        # ==========================================

        for reason in override_reasons:

            if reason not in findings:

                findings.append(reason)


        # ==========================================
        # 12. RESOURCE FINDINGS
        # ==========================================

        resource_findings = resource_result.get(
            "findings",
            []
        )


        # ==========================================
        # 13. FINAL RESULT
        # ==========================================

        return {

            "vital_agent":
                vital_result,

            "symptom_agent":
                symptom_result,

            "risk_agent":
                risk_result,

            "ml_model":
                ml_result,

            "resource_agent":
                resource_result,

            "final_priority":
                final_priority,

            "initial_priority":
                initial_priority,

            "safety_override":
                safety_override,

            "override_reasons":
                override_reasons,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "scores":
                scores,

            "findings":
                findings,

            "resource_findings":
                resource_findings
        }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    patient = {

        "temperature": 38.5,

        "heartrate": 125,

        "resprate": 28,

        "o2sat": 91,

        "sbp": 90,

        "dbp": 60,

        "pain_numeric": 8,

        "chiefcomplaint":
            "FACIAL DROOP",

        "pain":
            "8"
    }


    coordinator = DecisionCoordinator()

    result = coordinator.analyze_patient(
        patient
    )


    print("\n========================================")
    print("      MULTI-AGENT TRIAGE SYSTEM")
    print("========================================")


    # ==========================================
    # AGENT RESULTS
    # ==========================================

    print("\n===== AGENT RESULTS =====")


    print(
        "Vital Signs Agent:",
        result["vital_agent"]["assessment"]
    )


    print(
        "Symptom Agent:",
        result["symptom_agent"]["assessment"]
    )


    print(
        "Risk Assessment Agent:",
        result["risk_agent"]["assessment"]
    )


    print(
        "ML Model:",
        result["ml_model"]["priority"],
        f"({result['ml_model']['confidence']}%)"
    )


    print(
        "Resource Availability Agent:",
        result["resource_agent"]["assessment"]
    )


    # ==========================================
    # COORDINATOR
    # ==========================================

    print("\n===== COORDINATOR =====")


    print(
        "Initial Priority:",
        result["initial_priority"]
    )


    print(
        "Final Priority:",
        result["final_priority"]
    )


    print(
        "Coordinator Confidence:",
        result["confidence"],
        "%"
    )


    # ==========================================
    # SAFETY OVERRIDE
    # ==========================================

    print(
        "Safety Override:",
        "YES"
        if result["safety_override"]
        else "NO"
    )


    if result["override_reasons"]:

        print(
            "\n===== SAFETY OVERRIDE REASONS ====="
        )

        for reason in result["override_reasons"]:

            print(
                "-",
                reason
            )


    # ==========================================
    # SCORES
    # ==========================================

    print("\n===== SCORES =====")


    for key, value in result["scores"].items():

        print(
            f"{key}: {value}"
        )


    # ==========================================
    # FINDINGS
    # ==========================================

    print(
        "\n===== COMBINED CLINICAL FINDINGS ====="
    )


    for finding in result["findings"]:

        print(
            "-",
            finding
        )


    # ==========================================
    # RESOURCES
    # ==========================================

    print(
        "\n===== RESOURCE INFORMATION ====="
    )


    for finding in result["resource_findings"]:

        print(
            "-",
            finding
        )