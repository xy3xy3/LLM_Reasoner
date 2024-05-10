import re

def contains_latex_logic(expression):
    # 正则表达式匹配 LaTeX 逻辑运算符
    pattern = r'\\(oplus|lor|land|exists|forall|rightarrow|leftrightarrow|neg)'
    
    # 检查是否存在匹配
    if re.search(pattern, expression):
        return True
    else:
        return False

# 测试函数
test_expressions = [
    "a \\oplus b",        # 应返回 True
    "c \\lor d",          # 应返回 True
    "e \\cap f",          # 应返回 False (非逻辑运算符)
    "x \\forall y",       # 应返回 True
    "\\neg p \\rightarrow q"  # 应返回 True
]

for exp in test_expressions:
    print(f"Expression: '{exp}' contains LaTeX logic symbols: {contains_latex_logic(exp)}")
