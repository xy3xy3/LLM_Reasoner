from configparser import ConfigParser
import os
import re
from openai import OpenAI
import requests

#读取配置文件
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.ini")
cf = ConfigParser()

cf.read('config.ini', encoding='utf-8')

client = OpenAI(
    api_key=cf.get('API', 'API_SECRET_KEY'),
    base_url=cf.get('API', 'BASE_URL'),
)

def llm_send(prompt, system_msg):
    global cf
    max_try = 5
    cur = 0
    while cur < max_try:
        try:
            response = (
                client.chat.completions.create(
                    model=cf.get('API', 'MODEL'),
                    messages=get_msg(prompt, system_msg),
                    # extra_body={"chatId": random.randint(10000, 99999)},
                    temperature=0.8,
                    max_tokens=1024,
                )
                .choices[0]
                .message.content
            )
            return response
        except Exception as e:
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
#报错函数，用于加入到发送的消息中
def error_msg(msg,new_msg,response:str):
    if new_msg in msg:
        return msg
    if response in msg or "Result:" in msg:
        msg += "\n"+new_msg
    else:
        #去除response空行，并每行加行号
        response = response.split("\n")
        #去除空的
        response = [x for x in response if x]
        response = [f"{i+1}. {response[i]}" for i in range(len(response))]
        response = "\n".join(response)
        msg += f"\nResult:\n```\n{response}\n```\n{new_msg}"
    return msg

# 处理返回的结果
def process_response(text:str):
     # 去除Markdown列表编号
    text = re.sub(r"-\s+", "", text, flags=re.MULTILINE)
    # 去除数字编号
    text = re.sub(r"\d+\.\s+", "", text, flags=re.MULTILINE)
    # 提取```代码块```的内容，并包含在处理后的文本中
    block = re.findall(r"<FOL>(.*?)</FOL>", text, re.DOTALL)
    block_content = "\n".join(block)
    # 如果存在代码块，则去除整个代码块的标记
    if block_content:
        text = block_content
    # 去除单引号，双引号
    text = text.replace("'", "").replace('"', "")
    # 去除注释
    text = re.sub(r"\s*//.*", "", text)
    # 去除\
    text = text.replace("\\", "")
    # 去除空行
    text = text.replace("\n\n", "\n")
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
    res = [x for x in res if x]
    return text,res
# 定义抽取知识函数
def get_knowledge(full_premises:str,list_premises:list):
    k_list = []
    k_dict = {}
    k_dict[full_premises] = fastgpt_knowledge(f"<NL>\n{full_premises}\n<NL>", 600, "66150951cf0f76694271ecea", 0.15)
    for k in k_dict[full_premises]:
        k_list.append(k)
    # 每个premise查询知识库，加到knowledege
    for premise in list_premises:
        k_dict[premise]= fastgpt_knowledge(f"<NL>\n{premise}\n<NL>", 400, "6615095ecf0f76694271ed0d", 0.2)
        #从知识库list中提取知识
        for k in k_dict[premise]:
            if k not in k_list:
                k_list.append(k)
    return k_list,k_dict
# 获取fastgpt的知识库
def fastgpt_knowledge(
    query: str,
    max_tokens: int,
    dataset_id: str,
    similarity: int = 0,
    search_mode: str = "embedding",
    using_rerank: bool = False,
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

    Returns:
    A string of concatenated questions and answers, separated by newlines.
    """
    global cf
    # API URL
    api_url = f"{cf.get('API', 'FASTPGT_URL')}/api/core/dataset/searchTest"

    # Headers including a placeholder for Authorization token
    headers = {
        "Authorization": f"Bearer {cf.get('API', 'FASTPGT_API_KEY')}",  # Placeholder token; replace with actual token
        "Content-Type": "application/json",
    }

    # Request body
    data = {
        "datasetId": dataset_id,
        "text": query,
        "limit": max_tokens,
        "similarity": similarity,
        "searchMode": search_mode,
        "usingReRank": using_rerank,
    }

    # Sending the POST request to the API
    response = requests.post(api_url, json=data, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        response_data = response.json().get("data", [])["list"]
        # print(response_data)
        # Process the response data
        result = []
        for item in response_data:
            result_line = f"\n{item['q']}{item['a']}\n"
            result.append(result_line)
        return result
    else:
        # Return an error message in case of a failed request
        return []
