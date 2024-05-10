import datetime
from .client import *

test = """

## Symbols Description: 
1. Logical Conjunction: `expr1 ∧ expr2`
   - First-order Logic Example: `∀x (Cat(x) ∧ Black(x))`
   - Description: All cats are black.
2. Logical Disjunction: `expr1 ∨ expr2`
   - First-order Logic Example: `Rain(tommorrow) ∨ Snow(tommorrow)`
   - Description: tommorrow is rain or snow.
3. Logical Exclusive Disjunction: `expr1 ⊕ expr2`
   - First-order Logic Example: `∃x (Day(x) ⊕ Night(x))`
   - Description: There exists a time that is either day or night.
4. Logical Negation: `¬expr1`
   - First-order Logic Example: `∀x ¬Fly(x)`
   - Description: For all x, x cannot fly.
5. Logical Implication: `expr1 → expr2`
   - First-order Logic Example: `∀x (Bird(x) → Fly(x))`
   - Description: For all x, if x is a bird, then x can fly.
6. Logical Biconditional: `expr1 ↔ expr2`
   - First-order Logic Example: `∀x (Bachelor(x) ↔ ¬Married(x))`
   - Description: For all x, x is a bachelor if and only if x is not married.
7. Logical Universal Quantification: `∀x`
   - First-order Logic Example: `∀x (Human(x) → Mortal(x))`
   - Description: For all x, if x is human, then x is mortal.
8. Logical Existential Quantification: `∃x`
   - First-order Logic Example: `∃x (Cat(x) ∧ White(x))`
   - Description: There exists at least one x such that x is a white cat.
   """
origin = """# Role: Logic Translater
## For FOL rule generation
1. You SHOULD USE the following logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence)
2. You *SHOULD NEVER USE* the following symbols for FOL: "", "̸=", "%", "=" 
3. The literals in FOL SHOULD ALWAYS have predicate and entities, e.g., "Rounded(x, y)" or "City(guilin)"; expressions such as "y = a ∨ y = b" or "a ∧ b ∧ c" are NOT ALLOWED 
4. The FOL rule SHOULD ACCURATELY reflect the meaning of the NL statement 
5. You SHOULD ALWAYS put quantifiers and variables at the beginning of the FOL 
6. You SHOULD generate FOL rules with either: 
(1) no variables; (2) one variable "x"; (3) two variables "x", "y"; or (4) three variables "x", "y" and "z"
## Example to learn
{knowledge}
## Current task:
Convert the following {length} lines natural language sentences into {length} first-order logical formulas.
The formulas you output in the <FOL> tag should correspond line by line with the content in the <NL> tag
<NL>
{full_premises}
</NL>
## Output format
Use <FOL> and </FOL> to wrap the FOL formulas.
Each line in the tag should be a single FOL formula.
You can analyze task during your output.But don't use natural language in the final <FOL> tag.

Let's think step by step.
"""


# Firstly, follow the rules and output your analysis of each line in the <NL> tag.
# The analysis should specify the quantifiers, predicates, and entities in the sentence.
# You should also try to focus on the Attention to each line's analysis.
# Secondly,write {length} FOL formulas in the following tag <FOL>.
def process(
    id: int, full_premises: str, list_premises: list, k_list: list, k_dict: dict
):
    global origin
    # 遍历每一个list在k_dict构建提示
    #  knowledge = ""
    #  for key, value in k_dict.items():
    #     knowledge += f"Examples for `{key}`\n"+ "\n".join(value) + "\n"
    knowledge = "\n".join(k_dict[full_premises])
    prompt = origin.format(
        knowledge=knowledge, length=len(list_premises), full_premises=full_premises
    )
    print(f"ID{id}总体翻译 {datetime.datetime.now()}: \n{prompt}")
    raw_response = llm_send(prompt, "")
    print(raw_response)
    if raw_response == "":
        return f"ID{id}回复为空", []
    str_res, list_res = process_response(raw_response)
    return str_res, list_res
