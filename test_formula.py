from validator.fix_formula import validate_formula


if __name__ == "__main__":
    s = "∀xx (Human(xx) → (Studies(x) ∨ Teaches(x)))"
    print(validate_formula(s))