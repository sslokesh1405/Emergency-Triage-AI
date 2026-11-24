import math


class VitalSignsAgent:
    """
    Analyzes patient vital signs and identifies
    potentially concerning physiological patterns.
    """

    def __init__(self):
        self.agent_name = "Vital Signs Agent"

    def analyze(self, patient):
        findings = []
        risk_score = 0

        # -----------------------------
        # Heart Rate
        # -----------------------------
        heart_rate = patient.get("heartrate")

        if heart_rate is not None:
            if heart_rate >= 120:
                findings.append("Very high heart rate")
                risk_score += 2
            elif heart_rate >= 100:
                findings.append("Elevated heart rate")
                risk_score += 1
            elif heart_rate < 50:
                findings.append("Low heart rate")
                risk_score += 2

        # -----------------------------
        # Oxygen Saturation
        # -----------------------------
        oxygen = patient.get("o2sat")

        if oxygen is not None:
            if oxygen < 90:
                findings.append("Critically low oxygen saturation")
                risk_score += 3
            elif oxygen < 94:
                findings.append("Low oxygen saturation")
                risk_score += 2

        # -----------------------------
        # Systolic Blood Pressure
        # -----------------------------
        sbp = patient.get("sbp")

        if sbp is not None:
            if sbp < 90:
                findings.append("Very low systolic blood pressure")
                risk_score += 3
            elif sbp < 100:
                findings.append("Low systolic blood pressure")
                risk_score += 1
            elif sbp >= 180:
                findings.append("Very high systolic blood pressure")
                risk_score += 2

        # -----------------------------
        # Diastolic Blood Pressure
        # -----------------------------
        dbp = patient.get("dbp")

        if dbp is not None:
            if dbp < 60:
                findings.append("Low diastolic blood pressure")
                risk_score += 1
            elif dbp >= 120:
                findings.append("Very high diastolic blood pressure")
                risk_score += 2

        # -----------------------------
        # Respiratory Rate
        # -----------------------------
        respiratory = patient.get("resprate")

        if respiratory is not None:
            if respiratory >= 30:
                findings.append("Very high respiratory rate")
                risk_score += 3
            elif respiratory >= 22:
                findings.append("Elevated respiratory rate")
                risk_score += 1
            elif respiratory < 10:
                findings.append("Low respiratory rate")
                risk_score += 2

        # -----------------------------
        # Temperature
        # -----------------------------
        temperature = patient.get("temperature")

        if temperature is not None:
            if temperature >= 39:
                findings.append("High temperature")
                risk_score += 2
            elif temperature < 35:
                findings.append("Low temperature")
                risk_score += 2

        # -----------------------------
        # Determine assessment
        # -----------------------------
        if risk_score >= 6:
            assessment = "HIGH"
        elif risk_score >= 3:
            assessment = "MODERATE"
        else:
            assessment = "LOW"

        return {
            "agent": self.agent_name,
            "assessment": assessment,
            "risk_score": risk_score,
            "findings": findings
        }


# ---------------------------------
# Test the agent
# ---------------------------------

if __name__ == "__main__":

    test_patient = {
        "temperature": 38.5,
        "heartrate": 125,
        "resprate": 28,
        "o2sat": 91,
        "sbp": 90,
        "dbp": 60
    }

    agent = VitalSignsAgent()

    result = agent.analyze(test_patient)

    print("\n===== VITAL SIGNS AGENT =====")
    print("Agent:", result["agent"])
    print("Assessment:", result["assessment"])
    print("Risk Score:", result["risk_score"])

    print("\nFindings:")

    for finding in result["findings"]:
        print("-", finding)