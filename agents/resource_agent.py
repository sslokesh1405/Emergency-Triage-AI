"""
Resource Availability Agent

Simulates hospital resource availability for the academic prototype.
This does NOT connect to a real hospital system.
"""


def assess_resources():

    # Simulated hospital resources
    resources = {
        "icu_beds": 3,
        "ventilators": 2,
        "emergency_doctors": 4,
        "emergency_nurses": 6
    }

    findings = []

    # Assess ICU beds
    if resources["icu_beds"] <= 0:
        findings.append("No ICU beds currently available")
    elif resources["icu_beds"] <= 2:
        findings.append("Limited ICU bed availability")
    else:
        findings.append("ICU beds available")

    # Assess ventilators
    if resources["ventilators"] <= 0:
        findings.append("No ventilators currently available")
    elif resources["ventilators"] <= 1:
        findings.append("Limited ventilator availability")
    else:
        findings.append("Ventilators available")

    # Assess doctors
    if resources["emergency_doctors"] <= 1:
        findings.append("Limited emergency doctor availability")
    else:
        findings.append("Emergency doctors available")

    # Assess nurses
    if resources["emergency_nurses"] <= 2:
        findings.append("Limited emergency nurse availability")
    else:
        findings.append("Emergency nurses available")

    # Overall resource status
    limited_resources = 0

    if resources["icu_beds"] <= 2:
        limited_resources += 1

    if resources["ventilators"] <= 1:
        limited_resources += 1

    if resources["emergency_doctors"] <= 1:
        limited_resources += 1

    if resources["emergency_nurses"] <= 2:
        limited_resources += 1

    if limited_resources >= 2:
        assessment = "LIMITED"
    else:
        assessment = "AVAILABLE"

    return {
        "agent": "Resource Availability Agent",
        "assessment": assessment,
        "resources": resources,
        "findings": findings
    }


if __name__ == "__main__":

    print("\n===== RESOURCE AVAILABILITY AGENT =====")

    result = assess_resources()

    print("Agent:", result["agent"])
    print("Assessment:", result["assessment"])

    print("\nResources:")

    for resource, value in result["resources"].items():
        print(f"- {resource}: {value}")

    print("\nFindings:")

    for finding in result["findings"]:
        print(f"- {finding}")