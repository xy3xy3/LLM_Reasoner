# 测试error_fix的有效性
import json
from llm.error_fixer import process
from validator.inference import inference

input_name = "./log/gpt-3.5-turbo-0125.jsonl"

def try_id(id: int):
    input_name = "./log/gpt-3.5-turbo-0125.jsonl"
    # 查找对应id的测试
    with open(input_name, "r", encoding="utf-8") as infile:
        for line in infile:
            data = json.loads(line)
            if data["id"] == id:
                list_premises = data["premises"]
                list_premises.append(data["conclusion"])
                full_premises = "\n".join(list_premises)
                list_res = data["response"]
                list_res.append(data["conclusion-AI"])
                str_res = "\n".join(list_res)
                str_res,list_res = process(data["id"],full_premises,list_premises,[],{},str_res,list_premises)
                break
#尝试读取same为False的数据
# with open(input_name, "r", encoding="utf-8") as infile:
#     lines = infile.readlines()
#     # 先根据premises数量排序
#     lines = sorted(lines, key=lambda x: len(json.loads(x)["premises"]))
#     for line in lines:
#         data = json.loads(line)
#         if data["same"]:
#             continue
#         list_premises = data["premises"]
#         list_premises.append(data["conclusion"])
#         full_premises = "\n".join(list_premises)
#         list_res = data["response"]
#         list_res.append(data["conclusion-AI"])
#         str_res = "\n".join(list_res)
#         str_res,list_res = process(data["id"],full_premises,list_premises,[],{},str_res,list_premises)
#         # str_res, list_res = process(data["id"], full_premises, list_premises, [], {}, str_res, list_res)
#         # data["conclusion-AI"] = list_res[-1]
#         # data["response"] = list_res[:-1]
#         # label, errmsg = inference(data)
#         # print(list_res)
#         # print(label == data["label"])
#         break

try_id(10)