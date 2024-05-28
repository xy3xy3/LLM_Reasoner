from validator.fix_formula import check_predicate_consistency
from .client import *
origin = """You are a good logic formula error fixer!
# Instructions
The formulas are first-order logic formulas.Here are logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence)
## Example 1
Inconsistent naming of contextual predicates
<NL>
All electric cars use batteries.
All recharging stations provide electricity.
Any battery cars requires recharging.
</NL>
<FOL>
∀x (ElectricCar(x) → UsesBatteries(x))
∀x (RechargingStation(x) → ProvidesElectricity(x))
∀x (BatteryCar(x) → RequiresRecharging(x))
</FOL>
In order to make the formula consistent, we need to change the predicate "BatteryCar" to "UsesBatteries"
<FOL>
∀x (ElectricCar(x) → UsesBatteries(x))
∀x (RechargingStation(x) → ProvidesElectricity(x))
∀x (UsesBatteries(x) → RequiresRecharging(x))
</FOL>
## Example 2
<NL>
All dogs bark.
All animals can move.
Anything that barks is an animal.
</NL>
<FOL>
∀x (Dog(x) → Barks(x))
∀x (Animal(x) → CanMove(x))
∀x (Barking(x) → IsAnimal(x))
</FOL>
The predicate "Barking" doesn't necessarily refer to dogs but is used as if it does.
<FOL>
∀x (Dog(x) → Barks(x))
∀x (Animal(x) → CanMove(x))
∀x (Barks(x) → IsAnimal(x))
</FOL>
## Example 3
<NL>
All humans are mortal.
All men are humans.
All mortals eventually die.
</NL>
<FOL>
∀x (Human(x) → Mortal(x))
∀x (Man(x) → Human(x))
∀x (MortalBeing(x) → WillDie(x))
</FOL>
The term "MortalBeing" is introduced without a clear linkage to "Mortal".
<FOL>
∀x (Human(x) → Mortal(x))
∀x (Man(x) → Human(x))
∀x (Mortal(x) → WillDie(x))
</FOL>
# Current tasks
<NL>\n{full_premises}\n</NL>
<FOL>\n{str_res}\n</FOL>
{errmsg}
## Output format
Use <FOL> and </FOL> to wrap the FOL formulas after fixed.
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
    print(f"ID{id}错误修复")
    f, errmsg = check_predicate_consistency(list_res, True)
    prompt = origin.format(full_premises=full_premises, str_res=str_res, errmsg=errmsg)
    print(prompt)
    raw_response = llm_send(prompt, "")
    if raw_response == "":
        return f"ID{id}回复为空", []
    str_res, list_res = process_response(raw_response)
    return str_res, list_res

