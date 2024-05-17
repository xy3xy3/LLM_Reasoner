import re

# 假设 text 是你的HTML或XML样本
text = """
# For FOL rule generation
1. You SHOULD USE the following logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence) 2. You *SHOULD NEVER USE* the following symbols for FOL: "", "̸=", "%", "=" 3. The literals in FOL SHOULD ALWAYS have predicate and entities, e.gg., "Rounded(x, y)" or "City(guilin)"; expressions such as "y = a ∨ y = b" or "a ∧ b ∧ c" are NOT ALLOWED 4. The FOL rule SHOULD ACCURATELY reflect the meaning of the NL statement 5. You SHOULD ALWAYS put quantifiers and variables at the beginning of the FOL 6. You SHOULD generate FOL rules with either: (1) no variables; (2) one variable "x"; (3) two variables "x", "y"; or (4) three variables "x", "y" and "z"

# How to fix possible errors:
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

# Background information:
<NL>
All rabbits are cute.
Some turtles exist.
An animal is either a rabbit or a squirrel.
If something is skittish, then it is not still.
All squirrels are skittish.
Rock is still.
Rock is a turtle or cute.
</NL>
The sentences in <FOL> tags are generated from the background information in <NL> tags.
<FOL>
∀x (Rabbit(x) → Cute(x))
∃x Turtle(x)
∀x (Animal(x) → (Rabbit(x) ∨ Squirrel(x)))
∀x (Skittish(x) → ¬Still(x))
∀x (Squirrel(x) → Skittish(x))
Still(rock)
Turtle(rock) ∨ Cute(rock)
</FOL>


# Task
Firstly, analyse the probably errors in the background information <FOL>.
You need to analyse the points on `How to fix possible errors` for each line of <FOL>.
Secondly, reply with the specified number(7) of fol formulas in the `<FOL></FOL>` tag.
Please note that your reply can only have one `<FOL></FOL>` tag
Let's think step by step."""
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

print(process_response(text, tagname="FOL"))
