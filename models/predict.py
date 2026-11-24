import joblib
import pandas as pd


MODEL_PATH = "models/triage_model.pkl"


class TriageModel:

    def __init__(self):
        self.model = joblib.load(MODEL_PATH)

    def predict(self, patient):

        features = {
            "temperature": patient.get("temperature"),
            "heartrate": patient.get("heartrate"),
            "resprate": patient.get("resprate"),
            "o2sat": patient.get("o2sat"),
            "sbp": patient.get("sbp"),
            "dbp": patient.get("dbp"),
            "pain_numeric": patient.get("pain_numeric")
        }

        data = pd.DataFrame([features])

        prediction = self.model.predict(data)[0]

        probability = self.model.predict_proba(data)[0]

        confidence = max(probability) * 100

        if prediction == 1:
            priority = "HIGH"
        else:
            priority = "LOW"

        return {
            "prediction": int(prediction),
            "priority": priority,
            "confidence": round(confidence, 2)
        }


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":

    patient = {
        "temperature": 38.5,
        "heartrate": 125,
        "resprate": 28,
        "o2sat": 91,
        "sbp": 90,
        "dbp": 60,
        "pain_numeric": 8
    }

    model = TriageModel()

    result = model.predict(patient)

    print("\n===== ML TRIAGE MODEL =====")
    print("Prediction:", result["prediction"])
    print("Priority:", result["priority"])
    print("Confidence:", result["confidence"], "%")