import json,sys

def decide(risk,test_status):
    risk=str(risk).lower()
    test_status=str(test_status).upper()

    if test_status!="PASS":
        return "REJECT"

    if risk.startswith("low"):
        return "AUTO_APPROVE"

    if risk.startswith("medium"):
        return "TESTER_APPROVED_AUTO_DEPLOY"

    if risk.startswith("high"):
        return "HUMAN_APPROVAL"

    return "HUMAN_APPROVAL"

if len(sys.argv)>2:
    print(decide(sys.argv[1],sys.argv[2]))
