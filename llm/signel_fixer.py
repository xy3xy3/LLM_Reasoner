import datetime
from .client import *
from validator.fix_formula import (
    check_conclusion,
    check_predicate_consistency,
    validate_formula,
)

origin = """# Role: Logic Corrector
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
## Example to learn
{knowledge}
## Background Information
<NL>
{full_premises}
</NL>
The formulas below may contain errors.
<FOL>
{str_res}
</FOL>
## Cureent task:
{error_msg}
Firstly,follow the rules above and reply your idea about the error message.
Secondly,write only one FOL formula for one line in the following tag <FOL> which like `<FOL>Your answer</FOL>`.
Let's think step by step."""


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
    print(f"\nID{id}单个修复 {datetime.datetime.now()}\n")
    max_attempts = 6  # 最大尝试次数
    err_msg = ""  # 错误信息
    fianl_res = []
    for i, res_text in enumerate(list_res):
        valid, msg = validate_formula(res_text)
        retry_count = 0
        # knowledge = ""  
        # for key, value in k_dict.items():
        #     if key == full_premises:
        #         continue
        #     knowledge += f"Examples for `{key}`\n"+ "\n".join(value) + "\n"
        # knowledge = "\n".join(k_dict[list_premises[i]])
        knowledge = """
<NL>
All people who regularly drink coffee are dependent on caffeine.
People either regularly drink coffee or joke about being addicted to caffeine.
No one who jokes about being addicted to caffeine is unaware that caffeine is a drug.
Rina is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug.
If Rina is not a person dependent on caffeine and a student, then Rina is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student. 
</NL>
<FOL>
∀x (Drinks(x) → Dependent(x))
∀x (Drinks(x) ⊕ Jokes(x))
∀x (Jokes(x) → ¬Unaware(x))
(Student(rina) ∧ Unaware(rina)) ⊕ ¬(Student(rina) ∨ Unaware(rina))
¬(Dependent(rina) ∧ Student(rina)) → (Dependent(rina) ∧ Student(rina)) ⊕ ¬(Dependent(rina) ∨ Student(rina))
</FOL>
<NL>
Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music.
Any choral conductor is a musician.
Some musicians love music.
Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
</NL>
<FOL>
Czech(miroslav) ∧ ChoralConductor(miroslav) ∧ Specialize(miroslav, renaissance) ∧ Specialize(miroslav, baroque)
∀x (ChoralConductor(x) → Musician(x))
∃x (Musician(x) → Love(x, music))
Book(methodOfStudyingGregorianChant) ∧ Author(miroslav, methodOfStudyingGregorianChant) ∧ Publish(methodOfStudyingGregorianChant, year1946)
</FOL>
<NL>
All eels are fish. 
No fish are plants. 
A thing is either a plant or animal.
Nothing that breathes is paper. 
All animals breathe.
If a sea eel is either an eel or a plant, then a sea eel is an eel or an animal.
</NL>
<FOL>
∀x  (Eel (x)→  Fish (x))
∀x  (Fish (x)→ ¬ Plant (x))
∀x ( Plant (x) ∨  Animal (x))
∀x  (Breathe (x)→ ¬ Paper (x))
∀x  (Animal (x)→  Breathe (x))
 Eel (seaEel) ⊕ Plant (seaEel) → Eel (seaEel) ∨ Animal (seaEel) 
</FOL>"""
        while not valid and retry_count < max_attempts:
            retry_count += 1
            # 重新构造仅包含当前正在处理的premise的提示信息
            err_msg = (
                f"<NL>\n{list_premises[i]}\n</NL>\n<FOL>\n{res_text}\n<FOL>\n{msg}."
            )
            prompt = origin.format(
                str_res=str_res,
                knowledge=knowledge,
                full_premises=full_premises,
                error_msg=err_msg,
            )
            print(f"ID{id}单个修复{datetime.datetime.now()}重新发送 {retry_count + 1}次尝试:\n {prompt}")
            raw_res = llm_send(prompt, "")
            if (raw_res == ""):
                return "空回复", []
            # 获取新的回复
            res_text, res_list = process_response(raw_res)
            if len(res_list)>1:
                err_msg = (
                f"<NL>\n{list_premises[i]}\n</NL>\n<FOL>\n{res_text}\n<FOL>\nYou can only reply one line pure formula."
                )
                continue
            # 更新验证结果
            valid, msg = validate_formula(res_text)
        # 将最终验证通过或重试结束后的结果添加到结果列表
        if not valid:
            print(f"\n最终还是失败 {msg}\n{res_text}")
        list_res[i] = res_text
        str_res = "\n".join(list_res)
        fianl_res.append(res_text)
    str_res = "\n".join(fianl_res)
    return str_res, fianl_res
