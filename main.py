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
        return ""
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
    # 解包参数
    line, temp_output_path = args
    data = process_data(line)
    if not data:
        return
    # 将处理后的数据写入对应进程的临时文件
    with open(temp_output_path, "a", encoding="utf-8") as temp_file:
        temp_file.write(data + "\n")
        temp_file.flush()
        os.fsync(temp_file.fileno())


def run_parallel(num_lines=0, r=False, num_processes=6):
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

    # 创建临时输出文件名列表
    temp_output_paths = [f"./log/part_{i}.jsonl" for i in range(num_processes)]
    # 清空或创建临时文件
    for path in temp_output_paths:
        open(path, "w").close()

    # 分块数据
    chunk_size = len(lines) // num_processes + (len(lines) % num_processes > 0)
    data_chunks = [lines[i : i + chunk_size] for i in range(0, len(lines), chunk_size)]

    # 创建进程池
    with Pool(num_processes) as pool:
        tasks = [(chunk, temp_output_paths[i]) for i, chunk in enumerate(data_chunks)]
        pool.map(process_data_chunk, tasks)

    # 合并临时文件
    with open(output_name, "w", encoding="utf-8") as outfile:
        for temp_path in temp_output_paths:
            with open(temp_path, "r", encoding="utf-8") as temp_file:
                outfile.write(temp_file.read())
            # 删除临时文件
            os.remove(temp_path)
# 合并所有文件
def merge_files():
    #查找log所有带part_的合并到res
    path = "./log"
    files = os.listdir(path)
    with open("./log/res.jsonl", "w", encoding="utf-8") as outfile:
        for file in files:
            if "part_" in file:
                with open(f"{path}/{file}", "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
                os.remove(f"{path}/{file}")

def process_data_chunk(args):
    chunk, temp_output_path = args
    for line in chunk:
        process_data_parallel((line, temp_output_path))

def run_rest(use_multiprocessing=False, num_processes=4):
    input_name = "./data/folio_fix.jsonl"
    output_name = "./log/res.jsonl"
    processed_ids = set()

    # 读取已处理的数据，建立已处理ID集合
    with open(output_name, "r", encoding="utf-8") as res_file:
        for line in res_file:
            data = json.loads(line)
            processed_ids.add(data["id"])

    with open(input_name, "r", encoding="utf-8") as infile:
        lines = [line for line in infile if json.loads(line)["id"] not in processed_ids]

    if use_multiprocessing:
        # 创建临时输出文件名列表
        temp_output_paths = [f"./log/part_{i}.jsonl" for i in range(num_processes)]
        # 清空或创建临时文件
        for path in temp_output_paths:
            open(path, "w").close()

        # 分块数据
        chunk_size = len(lines) // num_processes + (len(lines) % num_processes > 0)
        data_chunks = [lines[i : i + chunk_size] for i in range(0, len(lines), chunk_size)]

        # 创建进程池
        with Pool(num_processes) as pool:
            tasks = [(chunk, temp_output_paths[i]) for i, chunk in enumerate(data_chunks)]
            pool.map(process_data_chunk, tasks)

        # 合并临时文件到最终输出文件
        with open(output_name, "a", encoding="utf-8") as outfile:
            for temp_path in temp_output_paths:
                with open(temp_path, "r", encoding="utf-8") as temp_file:
                    outfile.write(temp_file.read())
                # 删除临时文件
                os.remove(temp_path)
    else:
        # 单进程处理
        with open(output_name, "a", encoding="utf-8") as outfile:
            for line in lines:
                result = process_data(line)
                if result:
                    outfile.write(result + "\n")
                    outfile.flush()  # 确保数据写入文件
                    os.fsync(outfile.fileno())  # 确保写入的内容被立即写入磁盘

def try_id(id: int):
    input_name = "./data/folio_fix.jsonl"
    output_name = "./log/res.jsonl"
    # 查找对应id的测试
    with open(input_name, "r", encoding="utf-8") as infile, open(
        output_name, "a", encoding="utf-8"
    ) as outfile:
        for line in infile:
            data = json.loads(line)
            if data["id"] == id:
                res = process_data(line)
                if res:
                    outfile.write(res + "\n")
                    outfile.flush()
                break


if __name__ == "__main__":
    # run_parallel()
    # merge_files()
    run_rest(1)
