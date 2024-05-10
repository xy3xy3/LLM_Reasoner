from validator.fix_formula import *


if __name__ == "__main__":
    s = "∀x (∀y (Read(x, y) → GainKnowledge(x)))"
    print(check_unnecessary_quantifiers(s))
    s = "∀x ∀y (Read(x, y) → GainKnowledge(x))"
    print(check_unnecessary_quantifiers(s))