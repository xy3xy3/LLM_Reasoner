import datetime
from .client import *
from validator.fix_formula import (
    check_conclusion,
    check_latex_nature_language,
    check_predicate_consistency,
)

origin = """# Role: Logic Corrector
## Goals
- Enhance the compatibility of First-order Logic (FOL) formulas with formal verification tools by ensuring syntactical correctness and adherence to formal logic syntax.
- Automatically identify and suggest corrections for common syntax errors in FOL formulas to facilitate their processing by logic verifiers.
## For FOL rule generation
1. You SHOULD USE the following logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence) 2. You *SHOULD NEVER USE* the following symbols for FOL: "", "̸=", "%", "=" 3. The literals in FOL SHOULD ALWAYS have predicate and entities, e.g., "Rounded(x, y)" or "City(guilin)"; expressions such as "y = a ∨ y = b" or "a ∧ b ∧ c" are NOT ALLOWED 4. The FOL rule SHOULD ACCURATELY reflect the meaning of the NL statement 5. You SHOULD ALWAYS put quantifiers and variables at the beginning of the FOL 6. You SHOULD generate FOL rules with either: (1) no variables; (2) one variable "x"; (3) two variables "x", "y"; or (4) three variables "x", "y" and "z"
## Output format
Use <FOL> and </FOL> to wrap the FOL formulas.
Each line in the tag should be a single FOL formula.
You can analyze task during your output.But don't use natural language in the final <FOL> tag.
Only signal <FOL> can be in your reply.
## Example to learn
{knowledge}
## Background Information
The FOL formulas should be one to one of each line.Don't mix two line into one formula.
<NL>
{full_premises}
</NL>
{err_msg}
## For FOL rule generation
1. You SHOULD USE the following logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence)
2. You *SHOULD NEVER USE* the following symbols for FOL: "", "̸=", "%", "=" 
3. The literals in FOL SHOULD ALWAYS have predicate and entities, e.g., "Rounded(x, y)" or "City(guilin)"; expressions such as "y = a ∨ y = b" or "a ∧ b ∧ c" are NOT ALLOWED 
4. The FOL rule SHOULD ACCURATELY reflect the meaning of the NL statement 
5. You SHOULD ALWAYS put quantifiers and variables at the beginning of the FOL 
6. You SHOULD generate FOL rules with either: 
(1) no variables; (2) one variable "x"; (3) two variables "x", "y"; or (4) three variables "x", "y" and "z"
## Task
Let's think step by step.
Firstly,follow the rules above and reply your idea to do this job.
Secondly,write {length} FOL formulas after fixed in the following tag <FOL>.
"""


def process(
    id: int,
    full_premises: str,
    list_premises: list,
    k_list: list,
    k_dict: dict,
    str_res: str,
    list_res: list,
):
    global origin
    print(f"ID{id}整体修复")
    # 从k_dict获取整体的知识
    knowledge = ""
    for k in k_dict[full_premises]:
        knowledge += k
    length = len(list_premises)
    max_attempts = length * 2  # 最大尝试次数
    send_attempts = 0  # 当前尝试次数
    err_msg = ""  # 错误信息
    while send_attempts < max_attempts:
        # 需要发送
        if err_msg != "":
            prompt = origin.format(
                full_premises=full_premises,
                err_msg=err_msg,
                length=length,
                knowledge=knowledge,
            )
            print(f"ID{id}整体修复 {datetime.datetime.now()}，开始发送消息: \n{prompt}")
            raw_response = llm_send(prompt, "")
            if raw_response == "":
                return f"ID{id}回复为空", []
            str_res, list_res = process_response(raw_response)
            err_msg = ""
        # 检查是否包含LaTeX符号或自然语言
        if check_latex_nature_language(str_res):
            print(
                f"ID{id}整体修复 {datetime.datetime.now()} 包含LaTeX符号或自然语言, 重新发送 {send_attempts + 1}次尝试: {str_res}"
            )
            send_attempts += 1
            err_msg = f"<FOL>\n{str_res}\n</FOL>\n This contains LaTeX symbols or natural language, which is not allowed. Please provide the response in the correct format.<FOL> tag must contain pure formulas.\n"
            continue
        # 检查长度是否一致
        len_list = len(list_res)
        if len_list != length:
            print(
                f"\n{id} 整体修复 {datetime.datetime.now()} 需要 {length} 个, 只返回{len(list_res)}个\n"
            )
            send_attempts += 1
            err_msg = f"<FOL>\n{str_res}\n</FOL>\nError: expected {length} formulas, but got {len(list_res)} in the <FOL> tag.\n"
            if len_list > length:
                err_msg += " Please remove the extra formulas."
            else:
                err_msg += " Please provide the missing formulas."
            continue
        # 最后两个一起处理
        # 检查谓词元数
        f, msg = check_predicate_consistency(list_res)
        if f == False:
            print(f"\n{id} 整体修复{datetime.datetime.now()} {msg}\n")
            err_msg += f"<FOL>\n{str_res}\n</FOL>\nError: {msg}.\n"
        # 检查结论使用了其他之前的谓词和常量
        f, msg = check_conclusion(list_res)
        if f == False:
            print(f"\n{id} 整体修复 {datetime.datetime.now()} {msg}\n")
            if "FOL" in err_msg:
                err_msg += f"\nError: {msg}"
            else:
                err_msg += f"<FOL>\n{str_res}\n</FOL>\nError: {msg}.\n"
        if err_msg != "":
            send_attempts += 1
            continue
        else:
            break
    # 返回修正的结果
    return str_res, list_res
