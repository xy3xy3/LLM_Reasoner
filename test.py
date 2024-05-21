import re

def get_param_from_list(expressions):
    # 正则表达式匹配谓词及其参数
    predicates_with_args_re = re.compile(r"(\w+)\(([^)]+)\)")
    
    # 用于存储所有谓词及其参数的字典
    all_predicates = {}
    
    # 用于存储只在前件中出现的谓词的list
    antecedent_only_predicates = []
    
    # 用于存储所有后件谓词的集合
    all_consequents = set()
    
    for expression in expressions:
        # 提取前件和后件
        parts = expression.split("→")
        if len(parts) != 2:
            continue  # 跳过不符合格式的表达式
        consequent = parts[1].strip()
        # 提取后件中的所有谓词
        consequent_predicates_with_args = predicates_with_args_re.findall(consequent)
        for predicate, args in consequent_predicates_with_args:
            all_consequents.add(predicate)
    print(all_consequents)
    for expression in expressions:
        # 提取前件和后件
        parts = expression.split("→")
        if len(parts) != 2:
            continue  # 跳过不符合格式的表达式
        
        antecedent = parts[0].strip()
        # 提取前件中的所有谓词
        antecedent_predicates_with_args = predicates_with_args_re.findall(antecedent)
        for predicate, args in antecedent_predicates_with_args:
            if predicate not in all_consequents:
                #加入list
                antecedent_only_predicates.append(predicate)
                
    
    return antecedent_only_predicates

# 测试函数
expressions = [
    "∀x (TalentShows(x) → Engaged(x))",
    "∀x (TalentShows(x) ∨ Inactive(x))",
    "∀x (Chaperone(x) → ¬Students(x))",
    "∀x (Inactive(x) → Chaperone(x))",
    "∀x (AcademicCareer(x) → Students(x))"
]

antecedent_only_predicates = get_param_from_list(expressions)
print("Predicates that appear only in the antecedent:", antecedent_only_predicates)