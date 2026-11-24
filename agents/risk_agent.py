class RiskAssessmentAgent:
    """
    Identifies overall high-risk clinical patterns
    from patient symptoms and vital signs.
    """

    def __init__(self):
        self.agent_name = "Risk Assessment Agent"

    def analyze(self, patient):

        findings = []
        risk_score = 0

        heart_rate = patient.get("heartrate")
        oxygen = patient.get("o2sat")
        sbp = patient.get("sbp")
        respiratory = patient.get("resprate")
        temperature = patient.get("temperature")
        complaint = str(
            patient.get("chiefcomplaint", "")
        ).lower()

        # --------------------------------
        # Cardiovascular risk
        # --------------------------------

        if heart_rate is not None and heart_rate >= 120:
            findings.append(
                "Significant tachycardia"
            )
            risk_score += 2

        if sbp is not None and sbp <= 90:
            findings.append(
                "Hypotension risk"
            )
            risk_score += 2

        # --------------------------------
        # Respiratory risk
        # --------------------------------

        if oxygen is not None and oxygen < 92:
            findings.append(
                "Reduced oxygen saturation"
            )
            risk_score += 2

        if respiratory is not None and respiratory >= 28:
            findings.append(
                "Significant respiratory distress indicator"
            )
            risk_score += 2

        # --------------------------------
        # Temperature risk
        # --------------------------------

        if temperature is not None:
            if temperature >= 39:
                findings.append(
                    "High fever"
                )
                risk_score += 1

            elif temperature < 35:
                findings.append(
                    "Abnormally low temperature"
                )
                risk_score += 2

        # --------------------------------
        # High-risk complaints
        # --------------------------------

        high_risk_terms = [
            "arrest",
            "intubated",
            "head bleed",
            "stroke",
            "facial droop",
            "seizure",
            "trauma",
            "confusion"
        ]

        for term in high_risk_terms:
            if term in complaint:
                findings.append(
                    f"High-risk complaint: {term}"
                )
                risk_score += 3
                break

        # --------------------------------
        # Overall risk
        # --------------------------------

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


# ======================================
# Test the Risk Assessment Agent
# ======================================

if __name__ == "__main__":

    test_patient = {
        "temperature": 38.5,
        "heartrate": 125,
        "resprate": 28,
        "o2sat": 91,
        "sbp": 90,
        "dbp": 60,
        "chiefcomplaint": "FACIAL DROOP",
        "pain": "8"
    }

    agent = RiskAssessmentAgent()

    result = agent.analyze(test_patient)

    print("\n===== RISK ASSESSMENT AGENT =====")
    print("Agent:", result["agent"])
    print("Assessment:", result["assessment"])
    print("Risk Score:", result["risk_score"])

    print("\nFindings:")

    for finding in result["findings"]:
        print("-", finding)