import os
from .client import get_knowledge
from .overall_fixer import process as of_process
from .signel_fixer import process as sf_process
from .overall_translator import process as ot_process
from .error_fixer import process as ef_process
from .singel_translator import process as st_process
from .il_translator import process as il_process
from .baseline import process as bl_process

def send(data):
    return send_err_fix(data)
def send_baseline(data):
    id = data["id"]
    premises = "\n".join(data["premises"])
    conclusion = data["conclusion"]
    return bl_process(id,premises,conclusion)
#带中间语言版本
def send_with_middle(data):
    id = data["id"]
    premises = "\n".join(data["premises"])
    conclusion = data["conclusion"]
    # 查询知识库
    full_premises = premises + "\n" + conclusion  # 将结论添加到premises的末尾
    list_premises = full_premises.split("\n")
    # 中间语言消息发送
    full_premises, list_premises = il_process(id,full_premises,list_premises,[],{})
    if list_premises == []:
        print(f"总体翻译失败，{str_res}")
        return []
    print(full_premises)
    k_list,k_dict = get_knowledge(full_premises,list_premises, 1)
    # 整体消息发送
    str_res, list_res = ot_process(id,full_premises,list_premises,k_list,k_dict)
    if list_res == []:
        print(f"总体翻译失败，{str_res}")
        return []
    # 整体修正
    str_res, list_res = of_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == [] or len(list_res) != len(list_premises):
        print(f"整体修正失败，{str_res}")
        return []
    str_res, list_res = sf_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == []:
        print(f"单个修正失败，{str_res}")
        return []
    return list_res
# 不带修复
def send_one_step(data):
    id = data["id"]
    premises = "\n".join(data["premises"])
    conclusion = data["conclusion"]
    # 查询知识库
    full_premises = premises + "\n" + conclusion  # 将结论添加到premises的末尾
    list_premises = full_premises.split("\n")
    # list_premises = []
    k_list,k_dict = get_knowledge(full_premises,list_premises, 1)
    # 整体消息发送
    str_res, list_res = ot_process(id,full_premises,list_premises,k_list,k_dict)
    if list_res == []:
        print(f"总体翻译失败，{str_res}")
        return []
    return list_res
# 三步走，先整体发，再整体修复，再单个修复
def send_three_step(data):
    id = data["id"]
    premises = "\n".join(data["premises"])
    conclusion = data["conclusion"]
    # 查询知识库
    full_premises = premises + "\n" + conclusion  # 将结论添加到premises的末尾
    list_premises = full_premises.split("\n")
    # list_premises = []
    k_list,k_dict = get_knowledge(full_premises,list_premises, 1)
    # 整体消息发送
    str_res, list_res = ot_process(id,full_premises,list_premises,k_list,k_dict)
    if list_res == []:
        print(f"总体翻译失败，{str_res}")
        return []
    # 整体修正
    str_res, list_res = of_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == [] or len(list_res) != len(list_premises):
        print(f"整体修正失败，{str_res}")
        return []
    str_res, list_res = sf_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == []:
        print(f"单个修正失败，{str_res}")
        return []
    return list_res
# 基于三段的基础带错误修复
def send_err_fix(data):
    id = data["id"]
    premises = "\n".join(data["premises"])
    conclusion = data["conclusion"]
    # 查询知识库
    full_premises = premises + "\n" + conclusion  # 将结论添加到premises的末尾
    list_premises = full_premises.split("\n")
    k_list,k_dict = get_knowledge(full_premises,list_premises,1)
    # 整体消息发送
    str_res, list_res = ot_process(id,full_premises,list_premises,k_list,k_dict)
    if list_res == []:
        print(f"总体翻译失败，{str_res}")
        return []
    # 整体修正
    str_res, list_res = of_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == [] or len(list_res) != len(list_premises):
        print(f"整体修正失败，{str_res}")
        return []
    # 单个修正
    str_res, list_res = sf_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == []:
        print(f"单个修正失败，{str_res}")
        return []
    str_res, list_res = ef_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == [] or len(list_res) != len(list_premises):
        print(f"llm修正失败，最终数量不一致")
        return []
    str_res, list_res = sf_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == []:
        print(f"单个修正失败，{str_res}")
        return []
    return list_res
# 单步的，暂时废弃
def send_singel(data):
    id = data["id"]
    premises = "\n".join(data["premises"])
    conclusion = data["conclusion"]
    # 查询知识库
    full_premises = premises + "\n" + conclusion  # 将结论添加到premises的末尾
    list_premises = full_premises.split("\n")
    k_list,k_dict = get_knowledge("",list_premises, 1)
    str_res, list_res = st_process(id,full_premises,list_premises,k_list,k_dict)
    if list_res == []:
        print(f"失败，{str_res}")
        return []
    # 整体修正
    str_res, list_res = of_process(id,full_premises,list_premises,[],{},str_res, list_res)
    if list_res == [] or len(list_res) != len(list_premises):
        print(f"整体修正失败，{str_res}")
        return []
    str_res, list_res = sf_process(id,full_premises,list_premises,k_list,k_dict,str_res, list_res)
    if list_res == []:
        print(f"单个修正失败，{str_res}")
        return []
    return list_res
