import datetime
import json
import os
import random
import time
from multiprocessing import Pool
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


def run_single(num_lines=0, r=False):
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
        # 获取文件创建时间
        ctime = os.path.getctime(output_name)
        # 修改名字
        os.rename(
            output_name,
            f"./log/res_{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(ctime))}.jsonl",
        )
    with open(input_name, "r", encoding="utf-8") as infile, open(
        output_name, "a", encoding="utf-8"
    ) as outfile:
        lines = infile.readlines()
        if r:
            random.shuffle(lines)
        if num_lines != 0:
            lines = lines[:num_lines]
        # lines = lines[21:101]
        for line in lines:
            result = process_data(line)
            if result:
                outfile.write(result + "\n")
                outfile.flush()  # 立即将缓冲区的内容写入文件
                os.fsync(outfile.fileno())  # 确保写入的内容被立即写入磁盘


def process_data_parallel(args):
    line, output_lock = args
    data = json.loads(line)
    print("开始执行：", data["id"], " 时间：", datetime.datetime.now())
    res = send(data)  # 假设这是已经定义好的函数
    print(res)
    if len(res) == 0:
        return None
    data["conclusion-AI"] = res[-1]
    data["response"] = res[:-1]
    predicates, constants = get_param_from_list(res)
    predicates = list(predicates.keys())
    data["predicates-AI"] = " ".join(predicates)
    data["constants-AI"] = " ".join(constants)
    label, errmsg = inference(data)
    data["label-AI"] = label
    data["errmsg"] = errmsg
    data["same"] = data["label-AI"] == data["label"]
    return json.dumps(data)


def run_parallel(num_lines=0, r=False, num_processes=4):
    input_name = "./data/folio_fix.jsonl"
    output_name = "./log/res.jsonl"
    if os.path.exists(output_name):
        ctime = os.path.getctime(output_name)
        os.rename(
            output_name,
            f"./log/res_{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(ctime))}.jsonl",
        )
    with open(input_name, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
        if r:
            random.shuffle(lines)
        if num_lines != 0:
            lines = lines[:num_lines]

    # 分块数据
    chunk_size = len(lines) // num_processes
    data_chunks = [lines[i : i + chunk_size] for i in range(0, len(lines), chunk_size)]

    # 创建进程池
    with Pool(num_processes) as pool:
        # 构造参数，包括文件锁
        tasks = [(chunk, output_name) for chunk in data_chunks]
        results = pool.map(process_data_chunk, tasks)

        # 处理结果并写入文件
        with open(output_name, "a", encoding="utf-8") as outfile:
            for result_chunk in results:
                for result in result_chunk:
                    if result:
                        outfile.write(result + "\n")
                        outfile.flush()
                        os.fsync(outfile.fileno())


def process_data_chunk(args):
    chunk, output_name = args
    results = []
    for line in chunk:
        result = process_data_parallel((line, None))  # 暂时不使用锁
        if result:
            results.append(result)
    return results


if __name__ == "__main__":
    run_parallel()
    # run_single()
