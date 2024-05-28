import datetime
from .client import *
from .prompt import proofwriter_example,folio_example
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
<NL>
{full_premises}
</NL>
## Output format
Use <FOL> and </FOL> to wrap the FOL formulas.
The formulas you output in the <FOL> tag should correspond line by line with the content in the <NL> tag.
Each line in the tag should be a single FOL formula.
You can analyze task during your output.But don't use natural language in the final <FOL> tag.

Let's think step by step.
"""


def process(
   id: int, full_premises: str, list_premises: list, k_list: list, k_dict: dict
):
   global origin
   # knowledge = folio_example
   knowledge = "\n".join(k_dict[full_premises])
   for key, value in k_dict.items():
      knowledge += f"Examples for `{key}`\n"+ "\n".join(value[:4]) + "\n"
   prompt = origin.format(
      knowledge=knowledge, length=len(list_premises), full_premises=full_premises
   )
   print(f"ID{id}总体翻译 {datetime.datetime.now()}: \n{prompt}")
   raw_response = llm_send(prompt, "", 0)
   print(raw_response)
   if raw_response == "":
      return f"ID{id}回复为空", []
   str_res, list_res = process_response(raw_response)
   return str_res, list_res
