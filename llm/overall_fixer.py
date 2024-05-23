import datetime
from .client import *
from validator.fix_formula import (
    check_conclusion,
    check_nature_language,
    check_predicate_consistency,
)

origin = """# Role: Logic Corrector
## Goals
- Enhance the compatibility of First-order Logic (FOL) formulas with formal verification tools by ensuring syntactical correctness and adherence to formal logic syntax.
- Automatically identify and suggest corrections for common syntax errors in FOL formulas to facilitate their processing by logic verifiers.
## For FOL rule generation
1. You SHOULD USE the following logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence)
2. You *SHOULD NEVER USE* the following symbols for FOL: "", "̸=", "%", "=" 
3. The literals in FOL SHOULD ALWAYS have predicate and entities, e.g., "Rounded(x, y)" or "City(guilin)"; expressions such as "y = a ∨ y = b" or "a ∧ b ∧ c" are NOT ALLOWED 
4. The FOL rule SHOULD ACCURATELY reflect the meaning of the NL statement 
5. You SHOULD ALWAYS put quantifiers and variables at the beginning of the FOL 
6. You SHOULD generate FOL rules with either: 
(1) no variables; (2) one variable "x"; (3) two variables "x", "y"; or (4) three variables "x", "y" and "z"
## Output format
Use <FOL> and </FOL> to wrap the FOL formulas.
Each line in the tag should be a single FOL formula.
You can analyze task during your output.But don't use natural language in the final <FOL> tag.
Only signal <FOL> can be in your reply.
## Example to learn
{knowledge}
## Cureent task:
<NL>
{full_premises}
</NL>
{err_msg}
Firstly,follow the rules above and reply your idea about the error message.
Secondly,write {length} FOL formulas after fixed in the following tag <FOL> which like `<FOL>Your answer</FOL>`.
Let's think step by step.
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
    # knowledge = ""
    # for key, value in k_dict.items():
    #    knowledge += f"Examples for `{key}`\n"+ "\n".join(value) + "\n"
    knowledge = "\n".join(k_dict[full_premises])
#     knowledge = """
# <NL>
# All people who regularly drink coffee are dependent on caffeine.
# People either regularly drink coffee or joke about being addicted to caffeine.
# No one who jokes about being addicted to caffeine is unaware that caffeine is a drug.
# Rina is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug.
# If Rina is not a person dependent on caffeine and a student, then Rina is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student. 
# </NL>
# <FOL>
# ∀x (Drinks(x) → Dependent(x))
# ∀x (Drinks(x) ⊕ Jokes(x))
# ∀x (Jokes(x) → ¬Unaware(x))
# (Student(rina) ∧ Unaware(rina)) ⊕ ¬(Student(rina) ∨ Unaware(rina))
# ¬(Dependent(rina) ∧ Student(rina)) → (Dependent(rina) ∧ Student(rina)) ⊕ ¬(Dependent(rina) ∨ Student(rina))
# </FOL>
# <NL>
# Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music.
# Any choral conductor is a musician.
# Some musicians love music.
# Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
# </NL>
# <FOL>
# Czech(miroslav) ∧ ChoralConductor(miroslav) ∧ Specialize(miroslav, renaissance) ∧ Specialize(miroslav, baroque)
# ∀x (ChoralConductor(x) → Musician(x))
# ∃x (Musician(x) → Love(x, music))
# Book(methodOfStudyingGregorianChant) ∧ Author(miroslav, methodOfStudyingGregorianChant) ∧ Publish(methodOfStudyingGregorianChant, year1946)
# </FOL>
# <NL>
# All eels are fish. 
# No fish are plants. 
# A thing is either a plant or animal.
# Nothing that breathes is paper. 
# All animals breathe.
# If a sea eel is either an eel or a plant, then a sea eel is an eel or an animal.
# </NL>
# <FOL>
# ∀x  (Eel (x)→  Fish (x))
# ∀x  (Fish (x)→ ¬ Plant (x))
# ∀x ( Plant (x) ∨  Animal (x))
# ∀x  (Breathe (x)→ ¬ Paper (x))
# ∀x  (Animal (x)→  Breathe (x))
#  Eel (seaEel) ⊕ Plant (seaEel) → Eel (seaEel) ∨ Animal (seaEel) 
# </FOL>"""

    length = len(list_premises)
    max_attempts = length * 2 + 4  # 最大尝试次数
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
        if check_nature_language(str_res):
            print(
                f"ID{id}整体修复 {datetime.datetime.now()} 包含LaTeX符号或自然语言, 重新发送 {send_attempts + 1}次尝试: {str_res}"
            )
            send_attempts += 1
            err_msg = f"<FOL>\n{str_res}\n</FOL>\nThe content in the <FOL> tag contains LaTeX symbols or natural language, which is not allowed.\nPlease provide the response in the correct format.<FOL> tag must contain pure formulas.\n"
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
            err_msg += f"You should also make sure the fixed {length} formulas are one to one correspondence with the natural language premises.\n"
            continue
        # 检查出现一模一样的公式
        for i in range(len(list_res) - 1):
            for j in range(i + 1, len(list_res)):
                if list_res[i] == list_res[j]:
                    print(
                        f"\n{id} 整体修复 {datetime.datetime.now()} 公式{i}和{j}一样\n"
                    )
                    err_msg += f"Error: formulas {i} and {j} are the same.\nPlease provide different formulas.\n"
        if err_msg != "":
            err_msg = "<FOL>\n{str_res}\n</FOL>\n"+err_msg
            send_attempts += 1
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
