import os
from .client import get_knowledge
from .overall_fixer import process as of_process
from .signel_fixer import process as sf_process
from .overall_translator import process as ot_process
from .error_fixer import process as ef_process
# 定义发送函数
def send(data):
    id = data["id"]
    premises = "\n".join(data["premises"])
    conclusion = data["conclusion"]
    # 查询知识库
    full_premises = premises + "\n" + conclusion  # 将结论添加到premises的末尾
    list_premises = full_premises.split("\n")
    k_list,k_dict = get_knowledge(full_premises,list_premises)
    # 整体消息发送
    str_res, list_res = ot_process(id,full_premises,list_premises,k_list,k_dict)
    if list_res == []:
        print(f"总体翻译失败，{str_res}")
        return []
    # 整体修正
    str_res, list_res = of_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == []:
        print(f"整体修正失败，{str_res}")
        return []
    if len(list_res) != len(list_premises):
        print(f"整体修正失败，最终数量不一致")
        return []
    # 单个修正
    str_res, list_res = sf_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == []:
        print(f"单个修正失败，{str_res}")
        return []
    # str_res, list_res = ef_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    # if list_res == []:
    #     print(f"llm错误修复失败，{str_res}")
    #     return []
    # if len(list_res) != len(list_premises):
    #     print(f"llm修正失败，最终数量不一致")
    #     return []
    # str_res, list_res = sf_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    # if list_res == []:
    #     print(f"单个修正失败，{str_res}")
    #     return []
    return list_res
