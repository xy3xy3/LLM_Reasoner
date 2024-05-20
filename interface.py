
import json
from llm.client import process_response
from validator.inference import inference
# Example instance for testing
instance = {
    "conclusion-AI": "A(a)",
    "response": [
        "∀x A(a)"
    ]
}

result, proof_path = inference(instance)
print(f"Result: {result}, Proof Path: {proof_path}")

#测试推理和label的一致性
# input_name = "./data/folio_fix.jsonl"
# eror_list = []
# with open(input_name, "r", encoding="utf-8") as infile:
#     lines = infile.readlines()
#     for line in lines:
#         data = json.loads(line)
#         data["response"] = data['premises-FOL']
#         data["conclusion-AI"] = data['conclusion-FOL']
#         label, errmsg = inference(data)
#         if label != data["label"]:
#             eror_list.append(data["id"])
# print(eror_list)