from z3 import *
import re
from .translate import *


def replace_const(z3_formula, constants_dict):
    next_index = 1 + len(constants_dict)

    z3_formula = "".join(z3_formula.split())
    pattern = r"\([^()]+?\)"

    arrays_set = re.findall(pattern, z3_formula)
    for arrays in arrays_set:
        arrays_modified = arrays
        constantss = arrays[1:-1].split(",")
        constantss.sort(key=len, reverse=True)
        for constant in constantss:
            if constant not in ["x", "y", "z", "t", "w", "v"]:
                if constant.lower().replace(" ", "") in constants_dict:
                    index = constants_dict[constant.lower()]
                else:
                    constants_dict[constant.lower().replace(" ", "")] = next_index
                    index = next_index
                    next_index += 1
                arrays_modified = arrays_modified.replace(constant, str(index))
        z3_formula = z3_formula.replace(arrays, arrays_modified)
    return z3_formula


def extract_predicates(formula, predicates_dict):
    formula = "".join(formula.split())
    pattern = r"([A-Z][\w-]*)\((.*?)\)"
    matches = re.findall(pattern, formula)

    for match in matches:
        predicate_name = match[0]
        variables = match[1].split(",")
        arity = len(variables)
        predicates_dict[predicate_name] = arity

    return predicates_dict


def translate_premises(response):
    premises = []
    i = 1
    for premise in response:
        premise = premise.replace(".", "")
        premises.append(translate(premise))

    return premises


def create_functions(predicates_dict):
    created_functions = []
    for name, arity in predicates_dict.items():
        sorts = [IntSort() for _ in range(arity)]
        sorts.append(BoolSort())
        globals()[name] = Function(name.lower(), *sorts)
        created_functions.append(name)
    return created_functions


def cleanup_functions(created_functions):
    for name in created_functions:
        if name in globals():
            del globals()[name]


def reason(
    premises,
    conclusion,
    constants_dict,
    predicates_dict,
    origin_premises,
    origin_conclusion,
):
    solver = Solver()
    solver.set(proof=True)  # Enable proof generation
    created_functions = create_functions(predicates_dict)
    x, y, z = Int("x"), Int("y"), Int("z")
    u, v, w = Int("u"), Int("v"), Int("w")
    for i, premise in enumerate(premises):
        premise = replace_const(premise, constants_dict)
        try:
            solver.add(eval(premise))
        except Exception as e:
            cleanup_functions(created_functions)
            return False,f"{i} {origin_premises[i]}\n{premise}\n 添加前提异常: {e}"
    conclusion = replace_const(conclusion, constants_dict)
    try:
        solver.add(Not(eval(conclusion)))
    except Exception as e:
        cleanup_functions(created_functions)
        return False,f"{origin_conclusion}  {conclusion}, 添加结论异常: {e}"

    print(premises)
    print(conclusion)
    result = solver.check()
    print(solver)
    del solver
    if result == unsat:
        # proof = solver.proof()
        proof = ""
        cleanup_functions(created_functions)
        return True, str(proof)  # Returning proof as string if unsat
    else:
        cleanup_functions(created_functions)
        return False, None  # No proof to return if not unsat


def inference(instance):
    constants_dict = {}
    predicates_dict = {}

    instance["conclusion-AI"] = (
        instance["conclusion-AI"].replace(".", "").replace("’", "")
    )
    for i in range(len(instance["response"])):
        instance["response"][i] = (
            instance["response"][i].replace(".", "").replace("’", "")
        )
        predicates_dict = extract_predicates(instance["response"][i], predicates_dict)
    predicates_dict = extract_predicates(instance["conclusion-AI"], predicates_dict)
    premises = translate_premises(instance["response"])
    conclusion = translate(instance["conclusion-AI"].replace(".", ""))
    print("常量",constants_dict,"谓词",predicates_dict)
    case1, proof1 = reason(
        premises,
        conclusion,
        constants_dict,
        predicates_dict,
        instance["response"],
        instance["conclusion-AI"],
    )
    case2, proof2 = reason(
        premises,
        "Not(" + conclusion + ")",
        constants_dict,
        predicates_dict,
        instance["response"],
        instance["conclusion-AI"],
    )
    predicates_dict.clear()
    constants_dict.clear()
    if not isinstance(case1, bool) or not isinstance(case2, bool):
        error_message = f"Error encountered. Case1: {case1}, Case2: {case2}"
        return "Error", error_message

    if case1 and not case2:
        return "True", str(proof1)  # Return proof
    elif not case1 and case2:
        return "False", str(proof2)  # Return proof
    else:
        return "Unknown", ""
