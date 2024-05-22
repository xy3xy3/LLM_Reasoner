import json

#检测jsonl中premises和premises-FOL数量是否一致

input_name = "./data/folio-train.jsonl"
eror_list = []
with open(input_name, "r", encoding="utf-8") as infile:
    lines = infile.readlines()
    for line in lines:
        res = json.loads(line)
        if len(res["premises"]) != len(res["premises-FOL"]):
            eror_list.append(res)
print(eror_list)