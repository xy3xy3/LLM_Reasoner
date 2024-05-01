from validator.fix_formula import validate_formula


if __name__ == "__main__":
    s = "∀x (SymphonyNo9(x) ∧ MusicPiece(x) → True)"
    print(validate_formula(s))