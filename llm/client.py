from configparser import ConfigParser
import json
import os
import re
import socket
from openai import OpenAI
import requests
import hashlib

# 禁用ipv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False

# 读取配置文件
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.ini")
cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../cache")
# 修正反斜杠
cache_dir = cache_dir.replace("\\", "/")
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
cf = ConfigParser()

cf.read("config.ini", encoding="utf-8")

client = OpenAI(
    api_key=cf.get("API", "API_SECRET_KEY"),
    base_url=cf.get("API", "BASE_URL"),
)
API_URL = (
    "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B"
)
headers = {"Authorization": "Bearer "+cf.get("API", "HF_KEY")}
def log(msg):
    #追加在error.log
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../error.log").replace("\\", "/")
    with open(log_path, "a", encoding='utf-8') as f:
        f.write(msg+"\n")
    print(msg)

def huggingface_send(prompt:str):
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "inputs": prompt,
        },
    )
    json = response.json()
    print(json)
    return json[0]["generated_text"]

def ollama_send(prompt:str):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "ri",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    json = response.json()
    return json["response"]

def llm_send(prompt:str, system_msg:str, temperature=0.7):
    global cf
    # if system_msg == "":
    #     system_msg = "You are a helpful assistant."
    max_try = 2
    cur = 0
    while cur < max_try:
        try:
            res = client.chat.completions.create(
                model=cf.get("API", "MODEL"),
                messages=get_msg(prompt, system_msg),
                # extra_body={"chatId": random.randint(10000, 99999)},
                temperature=temperature,
                stream=False,
                # max_tokens=1024,
            )
            # print(res)
            if res.choices[0].message.content:
                return res.choices[0].message.content
            return ""
        except Exception as e:
            if cur == max_try - 1:
                log(f"{prompt}\n{e}")
            print(f"llm_send报错 {cur + 1}次尝试: {e}")
            cur += 1
    return ""


# 从数据构造json
def get_msg(ymsg, smsg=""):
    if smsg == "":
        messages = [{"role": "user", "content": ymsg}]
    else:
        messages = [
            {"role": "system", "content": smsg},
            {"role": "user", "content": ymsg},
        ]
    # print(messages)
    # os._exit(1)
    return messages


# 获取历史对话，暂时无用
def get_history(history: list) -> str:
    res = ""
    for i, item in enumerate(history):
        if i % 2 == 0:
            res += "<NL>\n" + item + "\n</NL>\n"
        else:
            res += "<FOL>\n" + item + "\n</FOL>\n"
    return res


# 报错函数，用于加入到发送的消息中
def error_msg(msg, new_msg, response: str):
    if new_msg in msg:
        return msg
    if response in msg or "Result:" in msg:
        msg += "\n" + new_msg
    else:
        # 去除response空行，并每行加行号
        response = response.split("\n")
        # 去除空的
        response = [x for x in response if x]
        response = [f"{i+1}. {response[i]}" for i in range(len(response))]
        response = "\n".join(response)
        msg += f"\nResult:\n```\n{response}\n```\n{new_msg}"
    return msg


# 处理返回的结果
def process_response(text: str, tagname:str = "FOL"):
    # 去除空行
    text = text.replace("\n\n", "\n")
    # 去除Markdown列表编号
    text = re.sub(r"-\s+", "", text, flags=re.MULTILINE)
    # 去除数字编号
    text = re.sub(r"\d+\.\s+", "", text, flags=re.MULTILINE)
    # 提取```代码块```的内容，并包含在处理后的文本中
    pattern = fr"<{tagname}>([^<]*?)</{tagname}>"
    block = re.findall(pattern, text, re.DOTALL)
    #去除多余的\n和为空的内容
    block = [x.strip() for x in block if x]
    block_content = "\n".join(block)
    # 如果存在代码块，则去除整个代码块的标记
    if block_content:
        text = block_content
    # 去除单引号，双引号
    text = text.replace("'", "").replace('"', "")
    # 去除注释//
    text = re.sub(r"\s*//.*", "", text)
    # 去除注释#
    text = re.sub(r"\s*#.*", "", text)
    # 去除\
    text = text.replace("\\", "")
    # 替换一些不合法
    text = text.replace("∀x,y", "∀x ∀y")
    # 将方括号替换为普通括号
    text = text.replace("[", "(").replace("]", ")")
    # 如果有莫名其妙的最外层括号则去除
    # if text.startswith("(") and text.endswith(")"):
    #     text = text[1:-1]
    # 去除`
    text = text.replace("`", "")
    res = text.split("\n")
    # 去除空行，去除开头的空格
    res = [x.strip() for x in res if x]
    text = "\n".join(res)
    return text, res


def count_words(text):
    words = text.split()
    return len(words)


# 定义抽取知识函数
def get_knowledge(full_premises: str, list_premises: list, type: int = 0):
    global cf
    k_list = []
    k_dict = {}
    if full_premises != "":
        k_dict[full_premises] = fastgpt_knowledge(
                f"<NL>\n{full_premises}\n<NL>", 1200, 4, cf.get("API", "KNOW_F"), 0
            )  # 600,0.15
        for k in k_dict[full_premises]:
            k_list.append(k)
    if type == 0:
        return k_list, k_dict
    # 每个premise查询知识库，加到knowledege
    for premise in list_premises:
        count = count_words(premise)
        if count > 35:
            num = 5
        else:
            num = 4
        k_dict[premise] = fastgpt_knowledge(
            f"<NL>\n{premise}\n<NL>", 700, num, cf.get("API", "KNOW_S"), 0
        )  # 500 0.2
        # 从知识库list中提取知识
        for k in k_dict[premise]:
            if k not in k_list:
                k_list.append(k)
    return k_list, k_dict


# 计算请求的唯一键
def get_cache_key(query, max_tokens, nums, dataset_id, similarity, search_mode):
    key_data = f"{query}_{max_tokens}_{nums}_{dataset_id}_{similarity}_{search_mode}"
    return hashlib.md5(key_data.encode()).hexdigest()


# 写入缓存
def write_cache(cache_key, data):
    cache_file = os.path.join(cache_dir, f"{cache_key}.txt")
    # 创建文件
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write("\n".join(data))


# 读取缓存
def read_cache(cache_key):
    cache_file = os.path.join(cache_dir, f"{cache_key}.txt")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return []


# 获取fastgpt的知识库
def fastgpt_knowledge(
    query: str,
    max_tokens: int,
    nums: int,
    dataset_id: str,
    similarity: int = 0,
    search_mode: str = "embedding",
    using_rerank: bool = False,
    retries: int = 5,
) -> list:
    """
    Sends a request to the FastGPT API to search within a specified dataset and returns the top results
    formatted as a string with questions and answers concatenated, separated by newlines.

    Parameters:
    - query: The text query to search for.
    - max_tokens: The maximum number of tokens to return.
    - dataset_id: The ID of the dataset to search in.
    - similarity: The similarity threshold for search results (default is 0).
    - search_mode: The search mode, can be 'embedding' or other modes supported by the API (default is 'embedding').
    - using_rerank: Whether to use re-ranking on the search results (default is False).
    - retries: Number of retries in case of request failures.

    Returns:
    A list of concatenated questions and answers, separated by newlines.
    """
    cache_key = get_cache_key(
        query, max_tokens, nums, dataset_id, similarity, search_mode
    )

    # 读取缓存
    cached_result = read_cache(cache_key)
    if cached_result:
        return cached_result
    # API URL from configuration
    api_url = f"{cf.get('API', 'FASTPGT_URL')}/api/core/dataset/searchTest"

    # Headers including a placeholder for Authorization token
    headers = {
        "Authorization": f"Bearer {cf.get('API', 'FASTPGT_API_KEY')}",  # Placeholder token; replace with actual token
        "Content-Type": "application/json",
    }

    # Request body
    json_data = {
        "datasetId": dataset_id,
        "text": query,
        "searchMode": search_mode,
        "usingReRank": False,
        "limit": max_tokens,
        "similarity": similarity,
        "datasetSearchUsingExtensionQuery": False,
        "datasetSearchExtensionModel": "gpt-3.5-turbo-0125",
        "datasetSearchExtensionBg": "",
    }

    # Initialize a session
    session = requests.Session()
    session.headers.update(headers)  # Update session headers

    for attempt in range(retries):
        try:
            # Force using IPv4
            session.socket = socket.create_connection(
                (api_url.split("//")[1].split("/")[0], 80)
            )

            # Sending the POST request to the API
            response = session.post(api_url, json=json_data)

            # Check if the response is successful
            if response.status_code == 200:
                response_data = response.json().get("data", [])["list"]
                # Process the response data
                result = []
                # 只取nums个
                response_data = response_data[:nums]
                for item in response_data:
                    result_line = f"{item['q']}{item['a']}\n"
                    result.append(result_line)
                    # 写入缓存
                write_cache(cache_key, result)
                return result
            else:
                print(
                    f"Attempt {attempt + 1}: Failed {response.status_code}, error : {response.text} \n json_data {json_data}"
                )
        except Exception as e:
            print(f"fastgpt_knowledge Attempt {attempt + 1}: An error occurred - {e}")

    return []  # If all retries fail, return an empty list


if __name__ == "__main__":
    print(
        count_words(
            "Bonnie either both attends and is very engaged with school events and is a student who attends the school, or she neither attends and is very engaged with school events nor is a student who attends the school."
        )
    )
