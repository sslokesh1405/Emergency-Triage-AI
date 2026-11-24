class SymptomAgent:
    """
    Analyzes the patient's chief complaint and pain level
    to identify potentially serious emergency symptoms.
    """

    def __init__(self):
        self.agent_name = "Symptom Agent"

    def analyze(self, patient):

        complaint = str(
            patient.get("chiefcomplaint", "")
        ).lower()

        pain = patient.get("pain")

        findings = []
        risk_score = 0

        # -----------------------------
        # Critical emergency symptoms
        # -----------------------------

        critical_keywords = [
            "arrest",
            "resp arrest",
            "cardiac arrest",
            "intubated",
            "unresponsive",
            "head bleed",
            "stroke",
            "facial droop",
            "seizure",
            "trauma",
            "car vs pole",
            "mvc"
        ]

        for keyword in critical_keywords:
            if keyword in complaint:
                findings.append(
                    f"Emergency symptom detected: {keyword}"
                )
                risk_score += 3
                break

        # -----------------------------
        # Serious symptoms
        # -----------------------------

        serious_keywords = [
            "shortness of breath",
            "sob",
            "chest pain",
            "confusion",
            "dizziness",
            "dka",
            "bleeding",
            "abd pain"
        ]

        for keyword in serious_keywords:
            if keyword in complaint:
                findings.append(
                    f"Serious symptom detected: {keyword}"
                )
                risk_score += 2
                break

        # -----------------------------
        # Pain analysis
        # -----------------------------

        try:
            pain_value = float(pain)

            if pain_value >= 8:
                findings.append("Severe pain")
                risk_score += 2

            elif pain_value >= 5:
                findings.append("Moderate pain")
                risk_score += 1

        except (ValueError, TypeError):
            pass

        # -----------------------------
        # Assessment
        # -----------------------------

        if risk_score >= 5:
            assessment = "HIGH"

        elif risk_score >= 2:
            assessment = "MODERATE"

        else:
            assessment = "LOW"

        return {
            "agent": self.agent_name,
            "assessment": assessment,
            "risk_score": risk_score,
            "findings": findings
        }


# ==========================================
# Test the Symptom Agent
# ==========================================

if __name__ == "__main__":

    test_patient = {
        "chiefcomplaint": "FACIAL DROOP",
        "pain": "8"
    }

    agent = SymptomAgent()

    result = agent.analyze(test_patient)

    print("\n===== SYMPTOM AGENT =====")
    print("Agent:", result["agent"])
    print("Assessment:", result["assessment"])
    print("Risk Score:", result["risk_score"])

    print("\nFindings:")

    for finding in result["findings"]:
        print("-", finding)