
from llm.main import send


str = """There exists a patient (P) such that for all doctors (D), P likes D."""
data = {
    "id": 1,
    "premises": str.split("\n"),
    "conclusion": "For all patients (P), there does not exist a quack (Q) such that P likes Q."
}

res = send(data)
print(res)