
import json
from llm.client import process_response
from validator.inference import inference
raw_response = """
<FOL>
∀x (Nintendo(x) → ¬SupportPS4(x))
∀x (Pokemon(x) → Nintendo(x))
∀x (FIFA(x) → SupportPS4(x))
∀x (SoccerOnline(x) → FIFA(x))
∃x (SoldMoreThanOneMillion(x) ∧ LegendOfZelda(x))
¬InTop10(LegendOfZelda)
</FOL>
"""

str_res, list_res = process_response(raw_response)
data = {}
data["response"] = list_res[:-1]
data["conclusion-AI"] = list_res[-1]
print(inference(data))

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