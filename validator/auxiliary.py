import re

# 提取并替换formula中的常元，因为两个公式要共享谓词和常元，因此记录constants_dict
constants_dict = {}  # 存储已经出现的常元及其索引
next_index = 1  # 下一个可用的索引
times = 0
def replace_const(z3_formula):
    global next_index
    global times
    if times == 2:
        next_index = 1
        constants_dict.clear()
        times = 0

    z3_formula = "".join(z3_formula.split())
    pattern = r'\([^()]+?\)'    # 匹配最小括号，其中不包含其他括号
    
    # 匹配字符串中的所有可能的常元
    arrays_set = re.findall(pattern, z3_formula)
    for arrays in arrays_set:
        arrays_modified = arrays
        constants = arrays[1:-1].split(",")
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
    times += 1
    return z3_formula
# extra_const


# 提取一个公式的谓词集和常元
def extract_predicates_and_constants(formula):
    # 使用正则表达式来匹配谓词名称和其元数
    # 正则表达式的模式解释：
    # \w+ 匹配一个或多个字母数字字符（谓词名称）
    # \((.*?)\) 匹配括号中的内容，括号内的内容可能包含任意字符，使用非贪婪匹配
    formula = "".join(formula.split())
    pattern = r'([A-Z][\w-]*)\((.*?)\)'
    matches = re.findall(pattern, formula)

    predicates_dict = {}
    constants_set = set()
    for match in matches:
        predicate_name = match[0]  # 提取谓词名称
        variables = match[1].split(',')  # 提取括号内的变量，并用逗号分隔
        arity = len(variables)  # 计算变量的个数，即元数

        # 检查变量是否为常元
        for var in variables:
            if var.strip() not in ['x', 'y', 'z', 't', 'w', 'v']:
                constants_set.add(var.strip())
        predicates_dict[predicate_name] = arity

    return predicates_dict, list(constants_set)
# extract_predicates_and_constants(formula)


# 判断一个公式是否被括号包围
def contained(formula):
    if len(formula) > 0 and formula[0] == '(' and formula[-1] == ')':
        cnt = 1
        for i in range(1, len(formula)-1):
            if formula[i] == '(':
                cnt += 1
            elif formula[i] == ')':
                cnt -= 1
            if cnt == 0:
                return False
        return True
    return False
# contained(formula)


# 计算公式中的括号相等与否
def is_balanced_parentheses(formula):
    # 初始化左右括号计数器
    left_count = 0
    right_count = 0

    # 遍历表达式中的每个字符
    for char in formula:
        # 统计左右括号的数量
        if char == '(':
            left_count += 1
        elif char == ')':
            right_count += 1

        # 如果右括号的数量超过左括号，说明括号不匹配
        if right_count > left_count:
            return False
    
    # 最后检查左右括号的总数是否相等
    return left_count == right_count
# is_balanced_parentheses(formula)



    






