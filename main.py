import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coordinator.decision_coordinator import DecisionCoordinator
from explainability.xai_explainer import XAIExplainer


def analyze_patient(patient):

    # Initialize coordinator
    coordinator = DecisionCoordinator()

    # Analyze patient
    result = coordinator.analyze_patient(patient)

    # Generate explanation
    explainer = XAIExplainer()

    explanation = explainer.generate_explanation(result)

    return result, explanation


if __name__ == "__main__":

    print("\n========================================")
    print("     EMERGENCY TRIAGE AI SYSTEM")
    print("========================================")

    print("\nEnter Patient Information")
    print("----------------------------------------")

    try:

        temperature = float(
            input("Temperature (°C): ")
        )

        heartrate = float(
            input("Heart Rate (bpm): ")
        )

        resprate = float(
            input("Respiratory Rate (/min): ")
        )

        o2sat = float(
            input("Oxygen Saturation (%): ")
        )

        sbp = float(
            input("Systolic BP (mmHg): ")
        )

        dbp = float(
            input("Diastolic BP (mmHg): ")
        )

        pain = input(
            "Pain Level (0-10): "
        )

        chiefcomplaint = input(
            "Chief Complaint: "
        )

        # Convert pain to numeric value
        try:
            pain_numeric = float(pain)
        except ValueError:
            pain_numeric = 0

        patient = {

            "temperature": temperature,
            "heartrate": heartrate,
            "resprate": resprate,
            "o2sat": o2sat,
            "sbp": sbp,
            "dbp": dbp,
            "pain_numeric": pain_numeric,
            "pain": pain,
            "chiefcomplaint": chiefcomplaint
        }

        # Run complete pipeline
        result, explanation = analyze_patient(patient)

        print("\n\n========================================")
        print("          TRIAGE RESULT")
        print("========================================")

        print(
            "\nFINAL PRIORITY:",
            result["final_priority"]
        )

        print(
            "COORDINATOR CONFIDENCE:",
            result["confidence"],
            "%"
        )

        print("\n\n========================================")
        print("        XAI EXPLANATION")
        print("========================================")

        print(explanation)

        print("\n========================================")
        print("      ANALYSIS COMPLETED")
        print("========================================")

    except ValueError:

        print(
            "\nERROR: Please enter valid numeric values."
        )