class XAIExplainer:
    """
    Generates a human-readable explanation for
    the final triage recommendation.
    """

    def __init__(self):
        self.module_name = "Explainable AI Module"

    def generate_explanation(self, result):

        priority = result["final_priority"]

        ml_result = result["ml_model"]

        findings = result["findings"]

        # Resource information
        resource_result = result.get(
            "resource_agent",
            {}
        )

        resource_findings = result.get(
            "resource_findings",
            []
        )

        explanation = []

        # --------------------------------
        # Final decision
        # --------------------------------

        explanation.append(
            f"Final Triage Priority: {priority}"
        )

        explanation.append(
            f"ML Model Prediction: {ml_result['priority']} "
            f"with {ml_result['confidence']}% confidence"
        )

        # --------------------------------
        # Agent agreement
        # --------------------------------

        explanation.append("\nAgent Assessments:")

        explanation.append(
            f"- Vital Signs Agent: "
            f"{result['vital_agent']['assessment']}"
        )

        explanation.append(
            f"- Symptom Agent: "
            f"{result['symptom_agent']['assessment']}"
        )

        explanation.append(
            f"- Risk Assessment Agent: "
            f"{result['risk_agent']['assessment']}"
        )

        # --------------------------------
        # Resource assessment
        # --------------------------------

        if resource_result:

            explanation.append(
                f"- Resource Availability Agent: "
                f"{resource_result.get('assessment', 'UNKNOWN')}"
            )

        # --------------------------------
        # Clinical reasons
        # --------------------------------

        explanation.append(
            "\nKey Factors Influencing Decision:"
        )

        # Remove duplicate findings
        unique_findings = list(
            dict.fromkeys(findings)
        )

        for finding in unique_findings:

            explanation.append(
                f"- {finding}"
            )

        # --------------------------------
        # Resource information
        # --------------------------------

        if resource_findings:

            explanation.append(
                "\nHospital Resource Information:"
            )

            unique_resource_findings = list(
                dict.fromkeys(resource_findings)
            )

            for finding in unique_resource_findings:

                explanation.append(
                    f"- {finding}"
                )

        # --------------------------------
        # Overall explanation
        # --------------------------------

        if priority == "HIGH":

            explanation.append(
                "\nExplanation: Multiple independent "
                "clinical agents identified significant "
                "risk indicators. The ML model also "
                "supports the high-priority assessment. "
                "Hospital resource information is "
                "provided as additional decision-support "
                "information."
            )

        elif priority == "MODERATE":

            explanation.append(
                "\nExplanation: The participating agents "
                "identified moderate clinical risk "
                "indicators. The patient should receive "
                "appropriate clinical assessment and "
                "monitoring. Hospital resource information "
                "is provided as additional decision-support "
                "information."
            )

        else:

            explanation.append(
                "\nExplanation: No major high-risk "
                "indicators were identified by the "
                "participating clinical agents. "
                "Hospital resource information is "
                "provided as additional decision-support "
                "information."
            )

        return "\n".join(explanation)


# ==========================================
# TEST XAI MODULE
# ==========================================

if __name__ == "__main__":

    # Example coordinator output

    coordinator_result = {

        "final_priority": "HIGH",

        "confidence": 100.0,

        "ml_model": {
            "prediction": 1,
            "priority": "HIGH",
            "confidence": 80.0
        },

        "vital_agent": {
            "assessment": "HIGH"
        },

        "symptom_agent": {
            "assessment": "HIGH"
        },

        "risk_agent": {
            "assessment": "HIGH"
        },

        "resource_agent": {
            "assessment": "AVAILABLE"
        },

        "findings": [
            "Very high heart rate",
            "Low oxygen saturation",
            "Low systolic blood pressure",
            "Elevated respiratory rate",
            "Emergency symptom detected: facial droop",
            "Severe pain",
            "Significant tachycardia",
            "Hypotension risk",
            "Reduced oxygen saturation",
            "Significant respiratory distress indicator"
        ],

        "resource_findings": [
            "ICU beds available",
            "Ventilators available",
            "Emergency doctors available",
            "Emergency nurses available"
        ]
    }

    explainer = XAIExplainer()

    explanation = explainer.generate_explanation(
        coordinator_result
    )

    print("\n========================================")
    print("       EXPLAINABLE AI MODULE")
    print("========================================")

    print(explanation)