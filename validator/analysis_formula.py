from z3 import *
from translate import *
import re

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
        constants = arrays[1:-1].split(",")
        constants.sort(key=len, reverse=True)
        for constant in constants:
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
