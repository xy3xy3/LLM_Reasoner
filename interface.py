import json
from validator.inference import inference

# 测试原本的label能不能推出来
# input_name = "./data/folio_fix.jsonl"

# with open(input_name, "r", encoding="utf-8") as infile:
#     for line in infile:
#         data = json.loads(line)
#         data["response"] = data["premises-FOL"]
#         data["conclusion-AI"] = data["conclusion-FOL"]
#         label, errmsg = inference(data)
#         if label != data["label"]:
#             print(data["id"], label, data["label"], errmsg)
#             break


input_name = "./log/res.jsonl"

# 使用列表存储更新后的行
updated_lines = []

with open(input_name, "r", encoding="utf-8") as infile:
    for line in infile:
        data = json.loads(line)
        label, errmsg = inference(data)
        data["label-AI"] = label
        data["errmsg"] = errmsg
        data["same"] = data["label-AI"] == data["label"]
        # 将更新后的数据转换为字符串并添加到列表中
        updated_lines.append(json.dumps(data) + "\n")

# 一次性写入所有更新后的行
with open(input_name, "w", encoding="utf-8") as outfile:
    outfile.writelines(updated_lines)