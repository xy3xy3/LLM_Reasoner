import datetime
from .client import *
from validator.fix_formula import (
    check_conclusion,
    check_predicate_consistency,
    get_param_from_list,
    validate_formula,
)

p_f_t = """# Role: Logic Translater
## For FOL rule generation
1. You SHOULD USE the following logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence)
2. You *SHOULD NEVER USE* the following symbols for FOL: ">","<", "̸=", "%", "=" 
3. The literals in FOL SHOULD ALWAYS have predicate and entities, e.g., "Rounded(x, y)" or "City(guilin)"; expressions such as "y = a ∨ y = b" or "a ∧ b ∧ c" are NOT ALLOWED 
4. The FOL rule SHOULD ACCURATELY reflect the meaning of the NL statement 
5. You SHOULD ALWAYS put quantifiers and variables at the beginning of the FOL 
6. You SHOULD generate FOL rules with either: 
(1) no variables; (2) one variable "x"; (3) two variables "x", "y"; or (4) three variables "x", "y" and "z"

## Attention
### Use of the xor formula Note: 
Make sure that both cannot be used at the same time, such as happy or sad, man or woman, this should be used XOR.
<NL>
Human is either male or female.
</NL>
<FOL>
∀ x Male(x) ⊕ Female(x)
</FOL>
<NL>
John is either a naughty student or a quiet good student.
</NL>
<FOL>
naughty(John) ⊕ quiet(John)
</FOL>
### Predicate consistency:
Sometimes, some predicates between some different sentences are different, but the word similarity is very high, you can consider these predicates unified into a word, which can ensure the accuracy of reasoning.
<NL>
Humans have two legs.
Animals with two feet can walk
Humans can walk
</NL>
<FOL>
∀x Human(x) → Have2Legs(x)
∀x With2Feet(x) → walk(x)
∀x Human(x) → walk(x)
</FOL>
In this example, the second line of With2Feet(x) can be unified into Have2Legs(x), which becomes
<FOL>
∀x Human(x) → Have2Legs(x)
∀x Have2Legs(x) → walk(x)
∀x Human(x) → walk(x)
</FOL>
### Discourse domain issues:
The discourse domain refers to the set of all the individuals involved in a predicate. In different sentences, the discourse domain may be different, which can lead to inaccuracy in reasoning. Consider unifying the discourse domains in different sentences to ensure the accuracy of reasoning.
Example:
<NL>
All new iPhones are very expensive.
Some phones use MediaTek chips.
All iPhones use the iOS system.
A phone is either an Android system or an iOS system.
If a phone uses a Snapdragon chip, then it must be an Android system.
XiaoMi13 use Android system and Snapdragon chip.
</NL>
<FOL>
∀x (new(x) ∧  Iphone(x)) → Expensive(x)
∃x MobilePhone(x) → MediaTek(x)
∀x Iphone(x) → iOS(x)
∀x Android(x) ⊕ iOS(x)
∀x (Snapdragon(x) → Android(x))
Snapdragon(XiaoMi13) ∧ Android(XiaoMi13)
</FOL>
Domain analysis:
1.MobilePhone.
2.MobilePhone or electronic device.`MobilePhone` may be removed.
3.MobilePhone.
4.MobilePhone.
5.MobilePhone.
6.MobilePhone.
The 1,3,4,5 sentences have the same domain which is mobile phone.
So we can turn the 2nd sentence's domain from device to mobile phone.
And remove the predicate "MobilePhone"

After fixed:
<FOL>
∀x (new(x) ∧  Iphone(x)) → Expensive(x)
∃x MediaTek(x)
∀x Iphone(x) → iOS(x)
∀x Android(x) ⊕ iOS(x)
∀x (Snapdragon(x) → Android(x))
Snapdragon(XiaoMi13) ∧ Android(XiaoMi13)
</FOL>
## Example to learn
{knowledge}
## Background information
<NL>
{full_premises}
</NL>
<FOL>
{fol_premises}
</FOL>
If the `<FOL>` tag is not empty,consider the whole context to ensure constants and predicates are the same.
If you use pre-existing predicates, keep the number of predicates arguments you use the same as before.
```pre-existing predicates templates
{p_info}
```
## Current task:
Firstly, analyse current task: `{cur_premise}` with `Attention` and `Example to learn`.
Secondly, reply one formula of this task in `<FOL>` tag.
Let's think step by step.
"""

p_f_f = """# Role: Logic Corrector
## For FOL rule generation
1. You SHOULD USE the following logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence)
2. You *SHOULD NEVER USE* the following symbols for FOL: ">","<", "̸=", "%", "=" 
3. The literals in FOL SHOULD ALWAYS have predicate and entities, e.g., "Rounded(x, y)" or "City(guilin)"; expressions such as "y = a ∨ y = b" or "a ∧ b ∧ c" are NOT ALLOWED 
4. The FOL rule SHOULD ACCURATELY reflect the meaning of the NL statement 
5. You SHOULD ALWAYS put quantifiers and variables at the beginning of the FOL 
6. You SHOULD generate FOL rules with either: 
(1) no variables; (2) one variable "x"; (3) two variables "x", "y"; or (4) three variables "x", "y" and "z"
## Example to learn
{knowledge}
## Background Information
<NL>
{full_premises}
</NL>
<FOL>
{fol_premises}
</FOL>
## Current task:
Firstly,follow the rules above and show me your analysis of fixing current task: `{cur_premise}`.
Here are some infomation about what you need to fix:

{error_msg}

Secondly, use <FOL> and </FOL> to wrap the FOL formulas.
Only one line of FOL formula without other description is allowed in the tag.
Let's think step by step."""


def process(
    id: int,
    full_premises: str,
    list_premises: list,
    k_list: list,
    k_dict: dict,
):
    global origin
    max_attempts = 8  # 最大尝试次数
    err_msg = ""  # 错误信息
    fianl_res = []
    for i, cur_premise in enumerate(list_premises):
        # knowledge = (
        #     f"Examples for `{cur_premise}`\n" + "\n".join(k_dict[cur_premise]) + "\n"
        # )
        knowledge = "\n".join(k_dict[cur_premise])
        length = len(list_premises)
        p_dict,_=get_param_from_list(fianl_res)
        p_info = ""
        # 创建一个字母字典
        letters = {1: 'x', 2: 'y', 3: 'z'}

        # 遍历p_dict中的每一项
        for k, v in p_dict.items():
            # 根据v的值，从字母字典中获取相应数量的字母，并将它们用逗号分隔开
            params = ', '.join([letters[i] for i in range(1, v + 1)])
            # 将这些字母添加到k后面，形成一个形如k(x,y,z)的字符串
            p_str = f'{k}({params})'
            # 将这个字符串添加到p_info中
            p_info += p_str + '\n'
        if i == 0:
            prompt = p_f_t.format(
                p_info=p_info,
                knowledge=knowledge,
                length=length,
                full_premises=full_premises,
                cur_premise=cur_premise,
                fol_premises=f"//There will be {length} FOL formulas to be completed.",
            )
        else:
            prompt = p_f_t.format(
                p_info=p_info,
                knowledge=knowledge,
                length=length,
                full_premises=full_premises,
                cur_premise=cur_premise,
                fol_premises="\n".join(fianl_res)
                + f"\n//There will be {length - i} FOL formulas to be completed.",
            )
        if i == length - 1:
            prompt+="The current task is the last line of <NL>.You can only use the previous predicates and constants beacuse this NL is the conclusion of the whole context."
        print(f"ID{id}单个翻译 {datetime.datetime.now()}: \n{prompt}")
        raw_response = llm_send(prompt, "", 0.3)
        if raw_response == "":
            return f"ID{id}回复为空", []
        print(raw_response)
        str_res, list_res = process_response(raw_response)
        # 判断是否需要修复
        valid, msg = validate_formula(str_res)
        retry_count = 0
        while not valid and retry_count < max_attempts:
            retry_count += 1
            # 重新构造仅包含当前正在处理的premise的提示信息
            err_msg = (
                f"<NL>\n{list_premises[i]}\n</NL>\n<FOL>\n{str_res}\n<FOL>\n{msg}."
            )
            prompt = p_f_f.format(
                knowledge=knowledge,
                full_premises=full_premises,
                error_msg=err_msg,
                cur_premise=cur_premise,
                fol_premises="\n".join(fianl_res),
            )
            print(
                f"ID{id}单个修复{datetime.datetime.now()}重新发送 {retry_count + 1}次尝试:\n {prompt}"
            )
            raw_res = llm_send(prompt, "",0.3)
            if raw_res == "":
                return "空回复", []
            str_res, list_res = process_response(raw_res)
            if len(list_res) > 1:
                err_msg = f"<NL>\n{list_premises[i]}\n</NL>\n<FOL>\n{str_res}\n<FOL>\nYou can only reply one line pure formula."
                continue
            valid, msg = validate_formula(str_res)
        # 将最终验证通过或重试结束后的结果添加到结果列表
        if not valid:
            print(f"\n最终还是失败 {msg}\n{str_res}")
        fianl_res.append(str_res)
    str_res = "\n".join(fianl_res)
    return str_res, fianl_res
