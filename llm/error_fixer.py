# 由大模型充当错误修复器
from .client import *
from validator.fix_formula import (
    check_conclusion,
    check_latex_nature_language,
    check_predicate_consistency,
    validate_formula,
)

origin = """# Role: Logic Error Fixer

## Attention:
Please ensure that all FOL formulations not only are syntactically correct but also semantically aligned with the given natural language descriptions. Errors in translation or logical representation must be clearly identified and corrected.

## Definition:
First Order Logic (FOL) translation error checking: This process involves reviewing a set of FOL statements to ensure they correctly represent the corresponding natural language statements, making corrections where necessary.

## Goals:
1. Identify errors in the translation of natural language statements to FOL formulations.
2. Provide a clear list of identified errors using Markdown syntax.
3. Correct any identified errors and represent the corrected version with the <FOL> tag.
4. Emphasize the output of all FOL statements, replacing only those with identified errors.

## Constraints:
1. Avoid using disallowed symbols and formats in FOL.
2. Maintain the structural integrity of FOL while making corrections.
3. Ensure all corrections are logically sound and maintain the intended meaning of the original natural language.

## Output Format:
1. List all identified errors in Markdown format.
2. Display all FOL statements (num of {length}), marking corrected versions with the <FOL> tag.

## Error identification should focus on the following aspects
1. Should 'either' be translated as OR or XOR in the overall context
2. Is there a lack of predicate usage in a certain sentence that prevents smooth reasoning

## Workflows:
1. **Error Identification**
   - Review each FOL statement against its corresponding natural language description.
   - Identify any mismatches or errors in logical representation.
   - List these errors using Markdown syntax.

2. **Correction of FOL Statements**
   - Correct identified errors in FOL statements.
   - Replace erroneous statements with corrected versions, marked with <FOL>.

3. **Output Generation**
   - Provide a comprehensive list of all original and corrected FOL statements.
   - Ensure that corrections are clearly indicated and all statements are included in the output.
   - Your ouput of <FOL> should contains all the corrected FOL statements not just the fixed ones.

## Some addition errors you need to fix
{err_msg}

## task
<NL>
{full_premises}
</NL>
<FOL>\n{str_res}\n</FOL>
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
    print(f"ID{id}错误修复")
    # 从k_dict获取错误的知识
    knowledge = ""
    for k in k_dict[full_premises]:
        knowledge += k
    length = len(list_premises)
    max_attempts = 2 * length  # 最大尝试次数
    send_attempts = 0  # 当前尝试次数
    err_msg = ""  # 错误信息
    while send_attempts < max_attempts:
        # 需要发送
        prompt = origin.format(
            full_premises=full_premises,
            err_msg=err_msg,
            length=length,
            str_res=str_res,
        )
        print(f"ID{id}错误修复，开始发送消息: \n{prompt}")
        raw_response = llm_send(prompt, "")
        if raw_response == "":
            return f"ID{id}回复为空", []
        str_res, list_res = process_response(raw_response)
        err_msg = ""
        # 检查长度是否一致
        len_list = len(list_res)
        if len_list != length:
            print(f"\n{id} 错误修复，需要 {length} 个, 只返回{len(list_res)}个\n")
            send_attempts += 1
            err_msg = f"<FOL>\n{str_res}\n</FOL>\nError: expected {length} formulas, but got {len(list_res)}.\n"
            if len_list > length:
                err_msg += " Please remove the extra formulas."
            else:
                err_msg += " Please provide the missing formulas."
            continue
        # 最后两个一起处理
        # 检查谓词元数
        f, msg = check_predicate_consistency(list_res)
        if f == False:
            print(f"\n{id} 错误修复{msg}\n")
            err_msg += f"<FOL>\n{str_res}\n</FOL>\nError: {msg}.\n"
        # 检查结论使用了其他之前的谓词和常量
        f, msg = check_conclusion(list_res)
        if f == False:
            print(f"\n{id} 错误修复 {msg}\n")
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