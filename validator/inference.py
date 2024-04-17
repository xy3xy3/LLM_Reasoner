from z3 import *
import re
from .translate import *

# 提取并替换formula中的常元，因为同一组前提要共享常元，因此记录constants_dict
# region
constants_dict = {}  # 存储已经出现的常元及其索引
next_index = 1  # 下一个可用的索引
def dict_clear():
    global next_index
    next_index = 1
    constants_dict.clear()

def replace_const(z3_formula):
    global next_index

    z3_formula = "".join(z3_formula.split())
    pattern = r'\([^()]+?\)'    # 匹配最小括号，其中不包含其他括号
    
    # 匹配字符串中的所有可能的常元
    arrays_set = re.findall(pattern, z3_formula)
    for arrays in arrays_set:
        arrays_modified = arrays
        constantss = arrays[1:-1].split(",")
        constantss.sort(key=len, reverse=True)
        for constant in constantss:
            if constant not in ['x', 'y', 'z', 't', 'w', 'v']:
                # 如果常元已经在字典中，则使用其索引，否则为其分配一个新的索引
                if constant.lower().replace(" ", "") in constants_dict:
                    index = constants_dict[constant.lower()]
                else:
                    constants_dict[constant.lower().replace(" ", "")] = next_index
                    index = next_index
                    next_index += 1
                arrays_modified = arrays_modified.replace(constant, str(index))
# 将 formula 中的常元替换为索引
        z3_formula = z3_formula.replace(arrays, arrays_modified)
    return z3_formula
# endregion
# replace_const(z3_formula)


# 提取一个公式的谓词集
# region
predicates_dict = {}
def predicates_clear():
    predicates_dict.clear()
def extract_predicates(formula):
    # 使用正则表达式来匹配谓词名称和其元数
    # 正则表达式的模式解释：
    # \w+ 匹配一个或多个字母数字字符（谓词名称）
    # \((.*?)\) 匹配括号中的内容，括号内的内容可能包含任意字符，使用非贪婪匹配
    formula = "".join(formula.split())
    pattern = r'([A-Z][\w-]*)\((.*?)\)'
    matches = re.findall(pattern, formula)

    for match in matches:
        predicate_name = match[0]  # 提取谓词名称
        variables = match[1].split(',')  # 提取括号内的变量，并用逗号分隔
        arity = len(variables)  # 计算变量的个数，即元数

        predicates_dict[predicate_name] = arity

    return predicates_dict
# endregion
# extract_predicates(formula)


# 翻译response至z3能接受的形式
def translate_premises(response):
    premises = []
    i = 1
    for premise in response:
        premise = premise.replace('.', '')
        premises.append(translate(premise))

    return premises
# translate_premises(response)


# 为每个谓词符号创建函数
def create_functions(predicates_dict):
    for name, arity in predicates_dict.items():
        sorts = [IntSort() for _ in range(arity)]
        sorts.append(BoolSort())
        globals()[name] = Function(name.lower(), *sorts)
# create_functions(predicates_dict)
        

# 对于整个例子进行推理
def reason(premises, conclusion, predicates_dict,origin_premises,origin_conclusion):
    try:
        # 创建一个解析器
        solver = Solver()

        # 声明逻辑符号
        create_functions(predicates_dict)

        # 变元区
        x = Int('x')
        y = Int('y')
        z = Int('z')

        # 替换常元
        dict_clear()
        premises_after_replace = []
        for premise in premises:
            new_premise = replace_const(premise)
            premises_after_replace.append(new_premise)
        conclusion = replace_const(conclusion)

        # 添加前提到解析器
        i = 0
        for premise in premises_after_replace:
            try:
                # 尝试评估并添加前提
                solver.add(eval(premise))
            except Exception as e:
                # 如果出现问题，打印这个前提
                return f"{i} {origin_premises[i]}\n{premise}\n 异常: {e}"
            i+=1
        # 添加结论的否定到解析器
        # print(f"conclusion= ", end="")
        # print(conclusion)
        try:
            solver.add(Not(eval(conclusion)))
        except Exception as e:
            # 如果出现问题，打印这个前提
            return f"{origin_conclusion}  {conclusion}, 异常: {e}"

        # 检查是否存在解，如果不存在则前提无法推出结论
        if solver.check() == unsat:
            return True
        else:
            return False
    except SyntaxError as e:
        return f"SyntaxError.{e}"
    except Z3Exception as e:
        return f"Z3Exception.{e}"

def log(msg):
    #追加在error.log
    with open("error.log", "a", encoding='utf-8') as f:
        f.write(msg+"\n")
    print(msg)
    
# 封装，此函数接受一个完整的、以字典形式给出的例子，至少包含"response", "conclusion-AI"
def inference(instance):
    predicates = {}
    predicates_clear()
    # 替换原有的特殊符号
    instance["conclusion-AI"] = instance["conclusion-AI"].replace('.', '').replace('’', '')
    for i in range(len(instance["response"])):
        instance["response"][i] = instance["response"][i].replace('.', '').replace('’', '')
        predicates = extract_predicates(instance["response"][i])
    predicates = extract_predicates(instance["conclusion-AI"])

    premises = translate_premises(instance["response"])
    conclusion = translate(instance["conclusion-AI"].replace('.', ''))
    case1 = reason(premises, conclusion, predicates, instance["response"], instance["conclusion-AI"])
    case2 = reason(premises, "Not("+conclusion+")", predicates, instance["response"], instance["conclusion-AI"])
    # 如果不是bool类型，则记录
    if not isinstance(case1, bool):
        err_msg = f"""\n新错误\n结论：{instance["conclusion-AI"]}\n格式化结论：{conclusion}\n前提：{instance["response"]}\n格式化前提：{premises}\n错误：{case1}\n"""
        log(err_msg)
        return "Error",err_msg
    if not isinstance(case2, bool):
        err_msg = f"""\n新错误\n结论：{instance["conclusion-AI"]}\n前提：{instance["response"]}\n错误：{case2}\n"""
        log(err_msg)
        return "Error",err_msg
    
    if case1 and not case2:
        return "True",""
    elif not case1 and case2:
        return "False",""
    else:
        return "Unknown",""
# inference(instance)


# instance = {"conclusion-AI": "\u2200x (Using(CANCER_RESEARCHERS, CANCER_EFFECT_SIZE) \u2227 Determining(CANCER_RESEARCHERS, GENETIC_ALTERATIONS))", \
#             "response": ["Finding(CANCER_BIOLOGY, GENETIC_ALTERATIONS)", "\u2200x Ranking(CANCER_RESEARCHERS, x)", "P_VALUE"]}
# print(inference(instance))
if __name__ == "__main__":
    is_forall("∀x ((¬DependentOnCaffeine(x) ∧ ¬Student(x)) → ((DependentOnCaffeine(x) ∧ Student(x)) ∨ (¬DependentOnCaffeine(x) ∧ ¬Student(x)))")