

from .formula_format import quelle
from .translate import translate
from .inference import replace_const
import re
from z3 import *
# 预编译的正则表达式
predicates_with_args_re = re.compile(r'([A-Z][a-zA-Z0-9]*)\s*\(([^)]*)\)')
variable_re = re.compile(r'\b[x-z]{1,2}\b')
variable_constraint_re = re.compile(r'([∀∃])([x-z])')
constant_assignment_re = re.compile(r'([a-zA-Z]\w*|\d+)\s*([=≠]+)\s*([a-zA-Z]\w*|\d+)')
constant_comparations_re = re.compile(r'([a-zA-Z]\w*|\d+)\s*([<>≥≤]+)\s*([a-zA-Z]\w*|\d+)')

def get_param_from_list(expressions):
    predicate_dict = {}
    constant_list = list()

    for expression in expressions:
        predicates_with_args = predicates_with_args_re.findall(expression)
        for predicate, args in predicates_with_args:
            # 统计每个谓词的参数个数
            if predicate in predicate_dict:
                predicate_dict[predicate] = max(predicate_dict[predicate], len(re.split(r'\s*,\s*', args.strip())))
            else:
                predicate_dict[predicate] = len(re.split(r'\s*,\s*', args.strip()))

            # 处理常量
            args = re.split(r'\s*,\s*', args.strip())
            for arg in args:
                if not re.match(r'^[x-z]{1,2}', arg) and re.match(r'^[a-zA-Z0-9]', arg):
                    constant_list.append(arg)


    return predicate_dict, constant_list

def check_predicate_consistency(expressions:list):
    predicate_usage_details = {}
    constant_list = list()
    for expression_id, expression in enumerate(expressions):
        predicates_with_args = predicates_with_args_re.findall(expression)
        for predicate, args in predicates_with_args:
            if "(" in args:
                return False, f"{expression},`{predicate}` is error.Nested predicates are not allowed. You may try other predicates but not like f(g(x))."
            args_count = len(re.split(r'\s*,\s*', args.strip()))
            if predicate not in predicate_usage_details:
                predicate_usage_details[predicate] = [(expression_id, args_count, expression)]
            else:
                predicate_usage_details[predicate].append((expression_id, args_count, expression))
            # 处理常量
            args = re.split(r'\s*,\s*', args.strip())
            for arg in args:
                if not re.match(r'^[x-z]{1,2}', arg) and re.match(r'^[a-zA-Z0-9]', arg):
                    constant_list.append(arg)
    # 禁止出现同名常量与谓词，忽略大小写
    # 获取忽略大小写的列表
    constant_list = [constant.lower() for constant in constant_list]
    predicate_list = [predicate.lower() for predicate in predicate_usage_details.keys()]
    # 检查是否有重复的常量和谓词
    for constant in constant_list:
        if constant in predicate_list:
            return False, f"'{constant}' is used as both a predicate and a constant. You should use different names for predicates and constants."
    inconsistent_predicates = {}
    single_occurrence_predicates = []
    nested_predicates = []
    # 检查谓词一致性
    for predicate, usages in predicate_usage_details.items():
        # 检查元数是否超过2
        for _, count, _ in usages:
            if count > 2:
                return False, f"Predicate '{predicate}' has arity {count}. Predicates must have at most 2 arguments. A 3 arity predicates can be replaced by some 2 arity predicates."
        
        # if len(usages) == 1:
        #     single_occurrence_predicates.append((predicate, usages[0][0]))  # 记录谓词和其索引
            
        unique_arg_counts = set(count for _, count, _ in usages)
        if len(unique_arg_counts) > 1:
            inconsistent_predicates[predicate] = usages

        # 检查谓词重叠 禁止谓词叠加，重叠f(g(x))
        for i, expression in enumerate(expressions): 
            predicate_pattern = fr'\b{predicate}\s*\('
            for match in re.finditer(predicate_pattern, expression):
                args_start = match.end()
                args_end = expression.find(')', args_start)
                args = expression[args_start:args_end]
                nested_predicate_match = re.search(r'\b([A-Z][a-zA-Z]*)\s*\(', args)
                if nested_predicate_match:
                    nested_predicate = nested_predicate_match.group(1)
                    nested_position = args_start + nested_predicate_match.start()
                    nested_predicates.append(f"Line:{i+1} `{expression}`.Predicate `{predicate}` has nested predicates `{nested_predicate}` in its arguments at position {nested_position}. ")
     
    # 构造报告信息
    if inconsistent_predicates or single_occurrence_predicates or nested_predicates:
        msg_parts = []
        if nested_predicates:
            usage_details = ", ".join(nested_predicates)
            return False, f"{usage_details} .You may try other predicates but not like f(g(x))."
        elif inconsistent_predicates:
            msg = "Inconsistent arity in predicates: "
            details = []
            for predicate, occurrences in inconsistent_predicates.items():
                usage_details = ", ".join([f"expression {id+1} `{expr}` with arity {count}" for id, count, expr in occurrences])
                details.append(f"{predicate} has inconsistent arity: {usage_details}")
            msg_parts.append(msg + "; ".join(details))
        if single_occurrence_predicates:
            single_details = ", ".join([f"'{predicate}' only occurs in expression {index+1}" for predicate, index in single_occurrence_predicates])
            msg_parts.append(f"Predicates that occur only once: {single_details}.")
        return False, ". ".join(msg_parts)+"You should check for similar predicates and replace them with the same one to ensure that the reasoning can proceed correctly.\nYou should check for similar predicates and replace them with the same one to ensure that the reasoning can proceed correctly.Or you can reduce the number of predicates."
    else:
        return True, ""


def is_empty(formula):
    return formula == ""

def is_balanced_parentheses(formula):
    stack = []
    left_count = 0  # 新增变量，用于计数左括号
    right_count = 0  # 新增变量，用于计数右括号
    for i, char in enumerate(formula):
        if char == '(':
            stack.append(('left', i))
            left_count += 1
        elif char == ')':
            right_count += 1
            if stack and stack[-1][0] == 'left':
                stack.pop()
            else:
                stack.append(('right', i))
    return stack, left_count, right_count

def get_variables(formula):    
    return set(variable_re.findall(formula))


def is_variable_constrained(formula, variable):
    return variable_constraint_re.search(formula) is not None

def get_variable_constraints(formula):
    constraints = {}
    stack = []
    for i, char in enumerate(formula):
        if char in {'∀', '∃'}:
            # 找到量词后的第一个非空格字符，它可能是变量名的开始
            variable_start = i + 1
            while variable_start < len(formula) and formula[variable_start] == ' ':
                variable_start += 1
            
            # 确定变量名的结束位置
            variable_end = variable_start
            while variable_end < len(formula) and formula[variable_end].isalpha():
                variable_end += 1

            variable = formula[variable_start:variable_end]
            next_char_pos = formula.find('(', variable_end) if '(' in formula[variable_end:] else len(formula)
            stack.append((variable, i, next_char_pos))
        elif char == ')' and stack:
            for item in reversed(stack):
                if len(item) == 3:
                    variable, quantifier_pos, start_pos = item
                    constraints.setdefault(variable, []).append((start_pos, i))
                    stack.remove(item)
                    break

    for variable, quantifier_pos, start_pos in stack:
        constraints.setdefault(variable, []).append((start_pos, len(formula) - 1))

    return constraints


def find_constant_assignments(formula):
    assignments = []
    for match in constant_assignment_re.finditer(formula):
        start_position, end_position = match.span()
        assignments.append((match.group(), start_position, end_position))
    return assignments
def find_constant_comparations(formula):
    comparations = []
    for match in constant_comparations_re.finditer(formula):
        start_position, end_position = match.span()
        comparations.append((match.group(), start_position, end_position))
    return comparations
def check_latex_nature_language(formula:str):
    nature_check =  "forall" in formula or "..." in formula or ":" in formula or "rightarrow" in formula or "neg" in formula or "$" in formula
    latex_symbols = re.findall(r"\\[a-zA-Z]+", formula)  # 寻找\开头的LaTeX符号
    return nature_check or bool(latex_symbols)

def check_formula(formula):
    forbidden_vars = [r'\bu\b', r'\bv\b', r'\bw\b']
    for var in forbidden_vars:
        if re.search(var, formula):
            return False, f"Variable '{var[2:-2]}' is not allowed. Only 'x', 'y', and 'z' are allowed as variables."
    return True, ""
    
def check_unparameterized_predicates(formula):
    unparameterized_predicates_info = []
    for match in re.finditer(r'\b([A-Z][a-zA-Z]*)\b(?!\()', formula):
        # 排除前面有单词和左括号的情况，例如："Function(Predicate)"
        is_preceded_by_word_and_parenthesis = False
        if match.start() > 0:
            # 查找谓词前的字符，以确定是否被其他单词和左括号紧跟
            preceding_text = formula[:match.start()]
            if re.search(r'\w\($', preceding_text):
                is_preceded_by_word_and_parenthesis = True
        following_text = formula[match.end():]
        if re.match(r'\)', following_text):
            continue  # 如果谓词后紧跟右括号，则忽略这个谓词
        # 如果不是紧跟在“单词(”后面的谓词，则认为它是一个不带参数的谓词
        if not is_preceded_by_word_and_parenthesis:
            unparameterized_predicates_info.append((match.group(0), match.start(), match.end()-1))

    if unparameterized_predicates_info:
        details = '; '.join([f"'{name}' at position: {start}-{end}" for name, start, end in unparameterized_predicates_info])
        return False, f"Unparameterized predicates found: {details}. Predicates must have parameters."
    return True, ""
def check_conclusion(f_list:list):
    conclusion = f_list[-1]
    premises = f_list[:-1]
    p1,c1 = get_param_from_list(premises)
    p2,c2 = get_param_from_list([conclusion])
    # 检查前提和结论的谓词一致性
    for predicate, arity in p2.items():
        if predicate not in p1:
            return False, f"Predicate '{predicate}' in conclusion(the last line) is not found in premises.Change this predicate or other similiar predicates to be the same in order to match the premises."
        if p1[predicate] != arity:
            return False, f"Predicate '{predicate}' has inconsistent arity in premises and conclusion."
    # 检查前提和结论的常元一致性
    # for constant in c2:
    #     if constant not in c1:
    #         return False, f"Constant '{constant}' in conclusion(the last line) is not found in premises."
    return True, ""
        
def validate_formula(formula):
    if is_empty(formula):
        return True, ""
    check_res, check_msg = check_formula(formula)
    if not check_res:
        return False, check_msg

    # 检查自然语言 forall rightarrow latex，如果有，返回
    if check_latex_nature_language(formula):
        return False, "Contains LaTeX `$` or Nature language entities.You need to output pure formula.Please use `¬` for negation, `∧` for conjunction, `∨` for disjunction, `→` for implication, `↔` for biconditional, and `⊕` for exclusive disjunction (XOR)."
    
    # 替换清除量词跟变量之间的空格
    formula = re.sub(r'([∀∃])\s+([x-z])', r'\1\2', formula)
    # 在变量后面紧跟的量词加空格
    formula = re.sub(r'([x-z])([∀∃])', r'\1 \2', formula)
    # 检查括号是否匹配
    unbalanced_parentheses, left_count, right_count = is_balanced_parentheses(formula)
    if unbalanced_parentheses:
        left_unmatched = [str(pos) for side, pos in unbalanced_parentheses if side == 'left']
        right_unmatched = [str(pos) for side, pos in unbalanced_parentheses if side == 'right']
        error_message = f"Unbalanced parentheses. Total left count: {left_count}, right count: {right_count}."
        if left_unmatched:
            error_message += f" Unmatched left parenthesis at positions: {', '.join(left_unmatched)}."
        if right_unmatched:
            error_message += f" Unmatched right parenthesis at positions: {', '.join(right_unmatched)}."
        return False, error_message
    
      # 检查是否有常元赋值 x = mike
    constant_assignments = find_constant_assignments(formula)
    if constant_assignments:
        assignments_str = "; ".join([f"Matched '{a[0]}' from position {a[1]} to {a[2]}" for a in constant_assignments])
        return False, f"Illeagl assignments: {assignments_str}.You can't use x = something,try to use something(x) to replace it."
    # 检查比较 x > xx
    constant_comparations = find_constant_comparations(formula)
    if constant_comparations:
        comparations_str = "; ".join([f"Matched '{c[0]}' from position {c[1]} to {c[2]}" for c in constant_comparations])
        return False, f"Illeagl comparations: {comparations_str}.You can't use x > something,try to use predicate(x,something) to replace it."
    
    match = re.search(r'[≠=<>≥≤]', formula)
    if match:
        return False, f"Invalid symbols in `=<>≥≤` at position {match.start()}"
    predicates, constants = get_param_from_list([formula])
   # 禁止谓词叠加，重叠f(g(x)) 和 三元谓词
    for predicate, arity in predicates.items():
        if (arity > 2):
            return False, f"Predicate '{predicate}' has arity {arity}. Predicates must have at most 2 arguments.A 3 arity predicates can be replaced by some 2 arity predicates."
        predicate_pattern = fr'\b{predicate}\s*\('
        for match in re.finditer(predicate_pattern, formula):
            args_start = match.end()
            args_end = formula.find(')', args_start)
            args = formula[args_start:args_end]
            nested_predicate_match = re.search(r'\b([A-Z][a-zA-Z]*)\s*\(', args)
            if nested_predicate_match:
                nested_predicate = nested_predicate_match.group(1)
                nested_position = args_start + nested_predicate_match.start()
                return False, f"Predicate '{predicate}' has nested predicates '{nested_predicate}' in its arguments at position {nested_position}.You may try other predicates."

    # 检查是否包含不带参数的谓词
    valid, msg = check_unparameterized_predicates(formula)
    if not valid:
        return valid, msg




    # 检查每个变量是否被约束
    all_variables = get_variables(formula)
    constraints = get_variable_constraints(formula)
    for var in all_variables:
        if var not in constraints:
            # 如果变量未被约束
            position = formula.find(var)
            return False, f"Variable '{var}' is not properly constrained at position {position}.Use quantifiers '∀' or '∃' to constrain variables."

        # 检查约束是否合法
        for start, end in constraints[var]:
            # 确保约束范围内没有其他量词
            constraint_range = formula[start:end+1]
            if re.search(r'[∀∃]', constraint_range):
                return False, f"Variable '{var}' has an invalid constraint range at positions {start} to {end}."
  

    res = quelle(formula)
    if res == "Not-a-formula":
        return False, f"Not a formula: {res}."

    return True, ""

def solvaer_test(formula):
    str = translate(formula)
    solver = Solver
    # 变元区
    x = Int('x')
    y = Int('y')
    z = Int('z')
    str =replace_const(str)
    try:
        # 尝试评估并添加前提
        solver.add(eval(str))
    except Exception as e:
        # 如果出现问题，打印这个前提
        return f"异常: {e}"
if __name__ == "__main__":
    s = "¬(∃x (Departure(x) = Arrival(x)))"
    print(validate_formula(s))
    # s2 = [
    #       "∀x (Top10Game(x)",
    #      "Top10Game(Top10game)" ]
    # print(check_predicate_consistency(s2))