# 可能之后改成专门修复特定问题
# 修复同义词替换
from .client import *
from validator.fix_formula import (
    check_conclusion,
    check_predicate_consistency,
    find_singel_predicate,
    validate_formula,
)

origin = """You are a good logic fixer to find the erros in the FOL formulas.
# For FOL rule generation
1. You SHOULD USE the following logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence) 2. You *SHOULD NEVER USE* the following symbols for FOL: "", "̸=", "%", "=" 3. The literals in FOL SHOULD ALWAYS have predicate and entities, e.g., "Rounded(x, y)" or "City(guilin)"; expressions such as "y = a ∨ y = b" or "a ∧ b ∧ c" are NOT ALLOWED 4. The FOL rule SHOULD ACCURATELY reflect the meaning of the NL statement 5. You SHOULD ALWAYS put quantifiers and variables at the beginning of the FOL 6. You SHOULD generate FOL rules with either: (1) no variables; (2) one variable "x"; (3) two variables "x", "y"; or (4) three variables "x", "y" and "z"

# Background information:
The sentences in <FOL> tags are generated from the background information in <NL> tags. 
<NL>
{full_premises}
</NL>
<FOL>\n{str_res}\n</FOL>
{err_msg}

# Help
The following are possible modifications

## Predicate consistency:
Sometimes, some predicates between some different sentences are different, but the word similarity is very high, you can consider these predicates unified into a word, which can ensure the accuracy of reasoning.
<NL>
Humans have two legs.
An animal with 2 legs is a human.
</NL>
<FOL>
∀ x Human (x) → Have2Legs (x)
∃x With2Leg (x) → Human (x)
</FOL>
In this example, the second line of With2Leg (x) can be unified into Have2Leg (x), which becomes
<FOL>
∀ x Human (x) → Have2Legs (x)
∃X Have2Leg (x) → Human (x)
</FOL>

## Discourse domain issues:
The discourse domain refers to the set of all the individuals involved in a predicate. In different sentences, the discourse domain may be different, which can lead to inaccuracy in reasoning. Consider unifying the discourse domains in different sentences to ensure the accuracy of reasoning.
For example, let's say both sentences are about cats
<NL>
All cats are cute.
There are some cats are blue.
</NL>
<FOL>
∀ x Cat (x) → Cute (x)
∃x Blue (x)
</FOL>
In this example, the second line should be appended with Cat (x), which becomes
<FOL>
∀ x Cat (x) → Cute (x)
∃X Cat (x) → Blue (x)
</FOL>
Or remove Cat (x) from the first line and become
<FOL>
∀ x Cute (x)
∃x Blue (x)
</FOL>

# Task
Let's think step by step.
Firstly, analyse the probably errors in the background information <FOL>.
You need to analyse the points on `Help` for each line of <FOL>.
Secondly, reply with the specified number({length}) of fol formulas in the `<FOL></FOL>` tag. Please note that your reply can only have one `<FOL></FOL>` tag
"""

# You need to reply yuor analysis which is important for yuo to fix the errors correctly.
# When analyzing errors, consider each of the following points for each line of <FOL> in detail
# 1. Logic Operator Decision: Determine whether to use OR (inclusive, symbolized as ∨) or XOR (exclusive, symbolized as ⊕) in logical contexts. Use XOR when dealing with two mutually exclusive propositions, such as 'male or female', where only one can be true at any given time.

# 2. Predicate Redundancy and Necessity:
#    - Redundancy Check: Evaluate if the predicate is superfluous. For instance, if the domain implicitly defined by the quantifier already includes the attribute described by the predicate (e.g., if the domain of 'x' is persons, the predicate 'Human(x)' is redundant and should be removed).
#    - Necessity Check: Assess if there is a missing necessary predicate. If the implicit domain of 'x' does not inherently include an essential attribute, this predicate needs to be added (e.g., if the domain is human, ensure predicates defining essential human attributes are explicitly stated).
# This check should based on the context.
# If other lines have the predicate to describe something's domain, you should remove the predicate in this line or add the missing predicate in other lines.

# 3. Hidden Information in Language: Identify and integrate predicates that may not be explicitly stated but are essential for ensuring accurate logical reasoning. These predicates often represent attributes or characteristics assumed within natural language but not overtly mentioned.

# 4. Explicit Information in Language: Recognize and employ predicates necessary for substantiating the reasoning based on explicitly stated information in the text. This involves using predicates to affirm the type or category of an item or concept when such specifications are crucial for logical coherence.


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
    # 从k_dict获取整体的知识
    # knowledge = ""
    # for key, value in k_dict.items():
    #    knowledge += f"Examples for `{key}`\n"+ "\n".join(value) + "\n"
    length = len(list_premises)
    max_attempts = 2 * length  # 最大尝试次数
    send_attempts = 0  # 当前尝试次数
    err_msg = find_singel_predicate(list_res)  # 错误信息
    while send_attempts < max_attempts:
        # 需要发送
        prompt = origin.format(
            full_premises=full_premises,
            err_msg=err_msg,
            length=length,
            str_res=str_res,
            # knowledge=knowledge,
        )
        # print(prompt)
        # break
        print(f"ID{id}错误修复，开始发送消息: \n{prompt}")
        raw_response = llm_send(prompt, "")
        if raw_response == "":
            return f"ID{id}回复为空", []
        print(raw_response)
        str_res, list_res = process_response(raw_response)
        err_msg = ""
        # 检查长度是否一致
        len_list = len(list_res)
        if len_list != length:
            print(f"\n{id} 错误修复，需要 {length} 个, 只返回{len(list_res)}个\n")
            send_attempts += 1
            err_msg = f"## Some addition errors you need to fix\nError: expected {length} formulas, but got {len(list_res)} in the <FOL> tag.Make sure the formulas are one to one of NL.\n"
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
            if "FOL" in err_msg:
                err_msg = f"## Some addition errors you need to fix\n"
            err_msg += f"\nError: {msg}.\n"
        # 检查结论使用了其他之前的谓词和常量
        f, msg = check_conclusion(list_res)
        if f == False:
            print(f"\n{id} 错误修复 {msg}\n")
            if "FOL" in err_msg:
                err_msg += f"## Some addition errors you need to fix\nError: {msg}"
            else:
                err_msg += f"\nError: {msg}.\n"
        if err_msg != "":
            send_attempts += 1
            continue
        else:
            break
    return str_res, list_res