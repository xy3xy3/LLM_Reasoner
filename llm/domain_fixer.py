# 可能之后改成专门修复特定问题
# 修复同义词替换
from .client import *
from validator.formula_format import *
from validator.auxiliary import contained
from validator.fix_formula import get_param_from_list as arity_query
origin = """Background nature language: {nl}
Background formula: {formula}
Is '{predicate}' a noun?
Can '{Predicate}(x)' be interpreted as "x is/are a/an/a piece of/a kind of(etc.) {predicate}", and mean "x is one of {predicate}?\". 
First analyze the meaning of the predicate.
Then,you need to answer "True" or "False" and put it in the <bool></bool> tag, in the form of <bool>True</bool> or <bool>False</bool>."""

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
    print(f"ID{id}论域修复")
    result = find_antecedent_predicates(list_res[:-1], list_res[-1])
    n_pre_set = set()
    for predicate in result:
        # 查找predicate存在list_res的位置
        nl = ""
        formula = ""
        for i in range(len(list_res)):
            if predicate in list_res[i]:
                nl = list_premises[i]
                formula = full_premises[i]
                break
        prompt = origin.format(predicate=predicate, Predicate=predicate.capitalize(),nl=nl,formula=formula)
        # print(f"quering {predicate}.....")
        answer = llm_send(prompt, "")
        # print(answer)
        is_noun_list = re.findall(r'<bool>(.*?)</bool>', answer)
        if is_noun_list and is_noun_list[0].strip().lower() == "true":
            n_pre_set.add(predicate)
    for res in n_pre_set:
        list_res.append(f"∀x ({res}(x))")
    str_res = " ".join(list_res)
    return str_res, list_res

# 查找前提前件谓词
def find_antecedent_predicates(premises, conclusion):
    pattern = r"[A-Z][a-zA-Z0-9]*\("

    antecedent_ps = set()   # 前提前件谓词
    unantecede_ps = set()   # 前提非前件谓词
    conclusion_ps = set()   # 结论谓词
    prohibit = set()
    predicates, _ = arity_query(premises)

    for premise in premises:
        # print(premise)
        if not is_formula(premise):
            return set()
        premise = premise.replace(' ', '')
        if contained(premise):
            premise = premise[1:-1]
        
        if is_forall(premise) or is_existential(premise):
            premise = premise[2:]
            if contained(premise):
                premise = premise[1:-1]

            implies_result = is_implies(premise)
            if implies_result:
                connective, _ = implies_result
                antecedent = premise[:connective]
                consequent = premise[connective+1:]
                antecedent_prds = re.findall(pattern, antecedent)
                consequent_ps = re.findall(pattern, consequent)
                for predicate in antecedent_prds:
                    antecedent_ps.add(predicate.rstrip('('))
                for predicate in consequent_ps:
                    unantecede_ps.add(predicate.rstrip('('))
                if (len(antecedent_prds) == 1 and len(consequent_ps) == 1):
                    prohibit.add(antecedent_prds[0].rstrip('('))
            else:
                un_implies_pres = re.findall(pattern, premise)
                for predicate in un_implies_pres:
                    unantecede_ps.add(predicate.rstrip('('))
        else:
            un_implies_pres = re.findall(pattern, premise)
            for predicate in un_implies_pres:
                unantecede_ps.add(predicate.rstrip('('))

    # print(f"conclusion = {conclusion}")
    conclu_pres = re.findall(pattern, conclusion)
    for predicate in conclu_pres:
        conclusion_ps.add(predicate.rstrip('('))

    resultt = antecedent_ps.difference(unantecede_ps).difference(conclusion_ps).difference(prohibit)
    result = set()
    for predicate in resultt:
        if predicates[predicate] == 1:
            result.add(predicate)
    return result
