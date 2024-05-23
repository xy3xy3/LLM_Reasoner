# 测试error_fix的有效性
import json
from llm.error_fixer import process as error_fixer
from llm.domain_fixer import process as domain_fixer
from validator.fix_formula import get_param_from_list
from validator.inference import inference

input_name = "./log/5-23-dp-rag迭代.jsonl"
output_name = "./log/fix.jsonl"

def try_id(id: int):
    # 查找对应id的测试
    with open(input_name, "r", encoding="utf-8") as infile, open(
        output_name, "a", encoding="utf-8"
    ) as outfile:
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
                data["conclusion-AI"] = list_res[-1]
                data["response"] = list_res[:-1]
                predicates, constants = get_param_from_list(list_res)
                predicates = list(predicates.keys())
                data["predicates-AI"] = " ".join(predicates)
                data["constants-AI"] = " ".join(constants)
                label, errmsg = inference(data)
                data["label-AI"] = label
                data["errmsg"] = errmsg
                data["same"] = data["label-AI"] == data["label"]
                outfile.write(json.dumps(data) + "\n")
                outfile.flush()
                break
#尝试读取same为False的数据
with open(input_name, "r", encoding="utf-8") as infile, open(
        output_name, "a", encoding="utf-8"
    ) as outfile:
    lines = infile.readlines()
    # 先根据premises数量排序
    lines = sorted(lines, key=lambda x: len(json.loads(x)["premises"]))
    for line in lines:
        data = json.loads(line)
        # if data["same"]:
        #     continue
        list_premises = data["premises"]
        list_premises.append(data["conclusion"])
        full_premises = "\n".join(list_premises)
        list_res = data["response"]
        list_res.append(data["conclusion-AI"])
        str_res = "\n".join(list_res)
        str_res,list_res = domain_fixer(data["id"],full_premises,list_premises,[],{},str_res,list_res)
        data["conclusion-AI"] = list_res[-1]
        data["response"] = list_res[:-1]
        predicates, constants = get_param_from_list(list_res)
        predicates = list(predicates.keys())
        data["predicates-AI"] = " ".join(predicates)
        data["constants-AI"] = " ".join(constants)
        label, errmsg = inference(data)
        data["label-AI"] = label
        data["errmsg"] = errmsg
        data["same"] = data["label-AI"] == data["label"]
        outfile.write(json.dumps(data) + "\n")
        outfile.flush()
        print(f"ID{data['id']}修复完成 修复结果：{data['same']}")
        

# try_id(10)