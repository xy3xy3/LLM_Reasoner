import datetime
import json
import os
import random
import time
from llm.main import send
from validator.fix_formula import get_param_from_list
from validator.inference import inference
# 处理数据
def process_data(line):
    data = json.loads(line)
    print("开始执行：", data["id"], " 时间：", datetime.datetime.now())
    res = send(data)
    print(res)
    if len(res) == 0:
        return
    data["conclusion-AI"] = res[-1]
    data["response"] = res[:-1]
    predicates, constants = get_param_from_list(res)
    # 只取keys，获取str的predicates
    predicates = list(predicates.keys())
    data["predicates-AI"] = " ".join(predicates)
    # list变成str
    data["constants-AI"] = " ".join(constants)
    label, errmsg = inference(data)
    data["label-AI"] = label
    data["errmsg"] = errmsg
    data["same"] = data["label-AI"] == data["label"]
    return json.dumps(data)
def run_single(num_lines,r = False):
    """
    处理指定数量的行。

    参数:
    num_lines: int
        指定要处理的行数。
    """
    # 打开输入文件并处理指定数量的行。
    input_name = "./data/folio_fix.jsonl"
    output_name = "./log/res.jsonl"
    # 如果有输出文件，则修改旧文件为他的创建日期时间
    if os.path.exists(output_name):
        #获取文件创建时间
        ctime = os.path.getctime(output_name)
        #修改名字
        os.rename(output_name, f"./log/res_{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(ctime))}.jsonl")
    with open(input_name, "r", encoding="utf-8") as infile, open(output_name, "a", encoding="utf-8") as outfile:
        lines = infile.readlines()
        if r:
            random.shuffle(lines)
        lines = lines[:num_lines]
        # lines = lines[21:101]
        for line in lines:
            result = process_data(line)
            if result:
                outfile.write(result + "\n")
                outfile.flush()  # 立即将缓冲区的内容写入文件
                os.fsync(outfile.fileno())  # 确保写入的内容被立即写入磁盘
if __name__ == "__main__":
    run_single(1,0)