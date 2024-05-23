# 可能之后改成专门修复特定问题
# 修复同义词替换
from .client import *
from .domain_fixer import process as domain_process
from .consistent_fixer import process as consistent_process
origin = """You are a good logic formula error finder!
# Example
The formulas are first-order logic formulas.Here are logical operators: ⊕ (either or), ∨ (disjunction), ∧ (conjunction), → (implication), ∀ (universal), ∃ (existential), ¬ (negation), ↔ (equivalence)
Giving some formulas, you need to identify which type of the error is in the formula.
The types of errors are as follows:
## id:1
Domain Variable Meaning and Predicate Meaning Repetition
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
## id:2
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
# Current tasks
You should indentify the following types of errors with tag `<type>id</type>`:
<NL>\n{full_premises}\n</NL>
<FOL>\n{str_res}\n</FOL>
Only reply one type of id, and put it in the <type></type> tag, in the form of <type>id</type>.
If no specific error is found, reply "<type>0</type>".
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
    prompt = origin.format(full_premises=full_premises, str_res=str_res)
    raw_response = llm_send(prompt, "")
    res = re.findall(r'<type>(.*?)</type>', raw_response)
    # raw_response=""
    # res = ["1"]
    if not res or res[0] == "0":
        return str_res, list_res
    print(f"{full_premises}\n {str_res}\n 错误修复结果：{raw_response}")
    if res[0] == "1":
        # 调用论域修复
        return domain_process(id, full_premises, list_premises, k_list, k_dict, str_res, list_res)
    if res[0] == "2":
        # 调用同义词修复
        return consistent_process(id, full_premises, list_premises, k_list, k_dict, str_res, list_res)
