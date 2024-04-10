from .auxiliary import *


# 判断公式是否是谓词符号应用、否定式、合取式、析取式、异或式、蕴含式、量词形式的其中之一
def is_formula(formula):
    if contained(formula):
        formula = formula[1:-1]

    return is_predicate(formula) or \
            is_negation(formula) or \
            is_conjunction(formula) or \
            is_implies(formula) or\
            is_equi(formula) or \
            is_xor(formula) or\
            is_disjunction(formula) or \
            is_existential(formula) or \
            is_forall(formula)
# is_formula(formula)


# 判断一个公式是否是谓词符号形式
def is_predicate(formula):
    formula = "".join(formula.split())
    if contained(formula):
        formula = formula[1:-1]

    #不能以量词开头
    if len(formula) > 0 and formula[0] in ['∃', '∀', '¬']:
       return False
    
    # 最多只能有一对括号
    num_of_paren = formula.count('(')
    if num_of_paren > 1:
        return False
    
    # 如果公式中有二元符号，返回False
    if '→' in formula or '∧' in formula or '∨' in formula or '⊕' in formula or '↔' in formula:
        return False
    
    left_paren_index = 0
    if '(' in formula:
        left_paren_index = formula.index('(')

    # 判断是否有左右括号
    if contained(formula[left_paren_index:-1]):
        return True
    
    # 提取括号之间的部分，应为谓词符号
    predic = formula[:left_paren_index]
    
    # 检查谓词符号是否满足要求
    if not (len(predic) > 0 and predic[0].isupper()):
        return False
    
    return True
# is_predicate(formula)


# 判断一个公式是否是否定式
def is_negation(formula):
    formula = "".join(formula.split())
    if contained(formula):
        formula = formula[1:-1]
    if not is_balanced_parentheses(formula):
        return False
    
    # 检查公式是否以 "¬" 开头
    if formula.startswith('¬'):        
        # 如果第二个符号开始的子公式被括号包围，则是否定式
        if contained(formula[1:]):
            return True
        
        # 从第二个符号开始往后找其他连接词
        for i in range(1, len(formula)-1):
            if formula[i] in ['∧', '∨', '→', '⊕', '↔']:
                left_formula = formula[:i].strip()
                right_formula = formula[i+1:].strip()
                if is_formula(left_formula) and is_formula(right_formula):
                    return False
        return True
    return False
# is_negation


# 判断一个公式是不是合取式
def is_conjunction(formula):
    if is_xor(formula) or is_disjunction(formula) or is_implies(formula):
        return False
    formula = "".join(formula.split())
    if contained(formula):
        formula = formula[1:-1]
    if not is_balanced_parentheses(formula):
        return False
    
    # 对每个 ∧ 符号都进行检查
    for i in range(len(formula)):
        if formula[i] == '∧':
            # 检查 ∧ 符号的左右两边是否是公式
            left_formula = formula[:i].strip()
            if contained(left_formula):
                left_formula = left_formula[1:-1]
            right_formula = formula[i+1:].strip()
            if contained(right_formula):
                right_formula = right_formula[1:-1]
        
            # 如果左右两边都是公式，则是合取式
            if is_formula(left_formula) and is_formula(right_formula):
                return (i, True)
    return False
# is_conjunction(formula)


# 判断一个公式是不是异或式
def is_xor(formula):
    if is_disjunction(formula) or is_implies(formula):
        return False
    formula = "".join(formula.split())
    if contained(formula):
        formula = formula[1:-1]
    if not is_balanced_parentheses(formula):
        return False

    # 对每个 ∧ 符号都进行检查
    for i in range(len(formula)):
        if formula[i] == '⊕':
            # 检查 ∧ 符号的左右两边是否是公式
            left_formula = formula[:i].strip()
            if contained(left_formula):
                left_formula = left_formula[1:-1]
            right_formula = formula[i+1:].strip()
            if contained(right_formula):
                right_formula = right_formula[1:-1]
        
            # 如果左右两边都是公式，则是合取式
            if is_formula(left_formula) and is_formula(right_formula):
                return (i, True)
    return False
# is_xor(formula)


# 判断一个公式是否是析取式
def is_disjunction(formula):
    if is_implies(formula):
        return False
    formula = "".join(formula.split())
    if contained(formula):
        formula = formula[1:-1]
    if not is_balanced_parentheses(formula):
        return False
    
    # 对每个 ∨ 符号都进行检查
    for i in range(len(formula)):
        if formula[i] == '∨':
            # 检查 ∨ 符号的左右两边是否是公式
            left_formula = formula[:i].strip()
            if contained(left_formula):
                left_formula = left_formula[1:-1]
            right_formula = formula[i+1:].strip()
            if contained(right_formula):
                right_formula = right_formula[1:-1]
        
            # 如果左右两边都是公式，则是析取式
            if is_formula(left_formula) and is_formula(right_formula):
                return (i, True)
    return False
# is_disjunction(formula)


# 判断一个公式是否是蕴含式
def is_implies(formula):
    if is_equi(formula):
        return False
    formula = "".join(formula.split())
    if contained(formula):
        formula = formula[1:-1]
    if not is_balanced_parentheses(formula):
        return False
    
    for i in range(len(formula)):
        if formula[i] == '→':
            left_formula = formula[:i].strip()
            if contained(left_formula):
                left_formula = left_formula[1:-1]
            right_formula = formula[i+1:].strip()
            if contained(right_formula):
                right_formula = right_formula[1:-1]

            if is_formula(left_formula) and is_formula(right_formula):
                return (i, True)
    return False
# is_implies(formula)


# 判断一个公式是否是等价式
def is_equi(formula):
    formula = "".join(formula.split())
    if contained(formula):
        formula = formula[1:-1]
    if not is_balanced_parentheses(formula):
        return False
    
    for i in range(len(formula)):
        if formula[i] == '↔':
            left_formula = formula[:i].strip()
            if contained(left_formula):
                left_formula = left_formula[1:-1]
            right_formula = formula[i+1:].strip()
            if contained(right_formula):
                right_formula = right_formula[1:-1]

            if is_formula(left_formula) and is_formula(right_formula):
                return (i, True)
    return False
# is_implies(formula)

# 判断一个公式是否是存在式
def is_existential(formula):
    formula = "".join(formula.split())
    if formula.startswith('(∃x)'):
        formula = formula[1:3] + formula[4:]
    if contained(formula):
        formula = formula[1:-1]
    if not is_balanced_parentheses(formula):
        return False
    
    if formula.startswith('∃'):
        # 如果第三个符号开始的子公式被括号包围，则是存在式
        if contained(formula[2:]):
            return True
        
        # 从第三个符号开始往后找其他连接词
        for i in range(2, len(formula)-1):
            if formula[i] in ['∧', '∨', '→', '⊕', '↔']:
                left_formula = formula[:i].strip()
                right_formula = formula[i+1:].strip()
                if is_formula(left_formula) and is_formula(right_formula):
                    return False
        return True
    return False
# is_existential


# 判断一个公式是否是全称式
def is_forall(formula):
    formula = "".join(formula.split())
    if formula.startswith('(∀x)') or formula.startswith('(∃x)'):
        formula = formula[1:3] + formula[4:]
    if contained(formula):
        formula = formula[1:-1]
    if not is_balanced_parentheses(formula):
        return False
        
    if formula.startswith('∀'):
        # 如果第三个符号开始的子公式被括号包围，则是存在式
        if contained(formula[2:]):
            return True
        
        # 从第三个符号开始往后找其他连接词
        for i in range(2, len(formula)-1):
            if formula[i] in ['∧', '∨', '→', '⊕', '↔']:
                left_formula = formula[:i].strip()
                right_formula = formula[i+1:].strip()
                if is_formula(left_formula) and is_formula(right_formula):
                    return False
        return True
    return False
# is_forall(formula)


# 判断一个公式是什么形式
def quelle(formula):
    if contained(formula):
        formula = formula[1:-1]

    if is_predicate(formula):
        return f"{formula} is a Predciate"
    elif is_negation(formula):
        return f"{formula} is a Negation"
    elif is_equi(formula):
        return f"{formula} is a Equiv" 
    elif is_implies(formula):
        return f"{formula} is a Implies"
    elif is_conjunction(formula):
        return f"{formula} is a Conjunction"
    elif is_disjunction(formula):
        return f"{formula} is a Disjunction"
    elif is_xor(formula):
        return f"{formula} is a Xor"
    elif is_existential(formula):
        return f"{formula} is a Existential"
    elif is_forall(formula):
        return f"{formula} is a Forall"
    return "Not-a-formula"
# quelle(formula)


