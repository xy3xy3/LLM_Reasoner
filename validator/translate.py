from .formula_format import *


# 翻译一个公式至z3形式
def translate(formula):
    formula = "".join(formula.split())

    if contained(formula):
        formula = formula[1:-1]

    # 如果是谓词应用形式，则不翻译
    if is_predicate(formula):
        return formula

    # 等价式
    equi_info = is_equi(formula)
    if is_equi(formula):
        equi_position, _ = equi_info
        left_formula = formula[:equi_position].strip()
        if contained(left_formula):
            left_formula = left_formula[1:-1]
        right_formula = formula[equi_position+1:].strip()
        if contained(right_formula):
            right_formula = right_formula[1:-1]

        # 将等价式翻译为两个蕴含
        new_formula = "((" + left_formula + ")→(" + right_formula + "))∧((" + right_formula + ")→(" + left_formula + "))"
        return translate(new_formula)

    # 判断是否是蕴含式
    implies_info = is_implies(formula)
    if implies_info:
        # 获取→的位置和性质
        implies_position, _ = implies_info
        # 提取蕴含式的左右公式
        left_formula = formula[:implies_position].strip()
        if contained(left_formula):
            left_formula = left_formula[1:-1]
        right_formula = formula[implies_position+1:].strip()
        if contained(right_formula):
            right_formula = right_formula[1:-1]
        # 翻译并返回
        return "Implies(" + translate(left_formula) + ", " + translate(right_formula) + ")"

    # 判断是否是析取式
    disjunction_info = is_disjunction(formula)
    if disjunction_info:
        # 获取∨的位置和性质
        disjunction_position, _ = disjunction_info
        # 提取析取式的左右公式
        left_formula = formula[:disjunction_position].strip()
        if contained(left_formula):
            left_formula = left_formula[1:-1]
        right_formula = formula[disjunction_position+1:].strip()
        if contained(right_formula):
            right_formula = right_formula[1:-1]
        # 翻译并返回
        return "Or(" + translate(left_formula) + ", " + translate(right_formula) + ")"

    # 判断是否是异或式
    xor_info = is_xor(formula)
    if xor_info:
        # 获取异或符号位置
        xor_position, _ = xor_info
        # 提取左右公式
        left_formula = formula[:xor_position].strip()
        if contained(left_formula):
            left_formula = left_formula[1:-1]
        right_formula = formula[xor_position+1:].strip()
        if contained(right_formula):
            right_formula = right_formula[1:-1]
        # 添加前缀
        return "Xor(" + translate(left_formula) + ", " + translate(right_formula) + ")"

    # 判断是否是合取式
    conjunction_info = is_conjunction(formula)
    if conjunction_info:
        # 获取∧的位置和性质
        conjunction_position, _ = conjunction_info
        # 提取合取式的左右公式
        left_formula = formula[:conjunction_position].strip()
        if contained(left_formula):
            left_formula = left_formula[1:-1]
        right_formula = formula[conjunction_position+1:].strip()
        if contained(right_formula):
            right_formula = right_formula[1:-1]
        # 翻译并返回
        return "And(" + translate(left_formula) + ", " + translate(right_formula) + ")"

    # 如果是否定式
    if is_negation(formula):
        # 获取否定式的内部公式
        inner_formula = formula[1:].strip()
        if contained(inner_formula):
            inner_formula = inner_formula[1:-1].strip()
        # 递归翻译内部公式，并添加 "Not" 前缀
        return "Not(" + translate(inner_formula) + ")"

    # 如果是存在量词形式
    if is_existential(formula) or is_forall(formula):
        if formula.startswith('(∀x)') or formula.startswith('(∃x)'):
            formula = formula[1:3] + formula[4:]
        # 提取量词和内部公式
        quantifier = formula[0]
        if contained(formula[2:]):
            inner_formula = formula[3:-1].strip()
        else:
            inner_formula = formula[2:].strip()
        # 递归翻译内部公式，并添加 "Exists" 或 "ForAll" 前缀
        if quantifier == '∃':
            return f"Exists({formula[1]}, {translate(inner_formula)})"
        elif quantifier == '∀':
            return f"ForAll({formula[1]}, {translate(inner_formula)})"

    # 如果是其他情况，说明输入错误
    return f"-----{formula}-----"
