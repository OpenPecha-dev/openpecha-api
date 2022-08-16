from pathlib import Path

from symspellpy import SymSpell, Verbosity

ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent
DICTS_PATH = ROOT_PATH.parent / "grams" / "data" / "dictionaries"

assert DICTS_PATH.is_dir()


def test_dictionary(dic_name, input_term, input_phrase):
    dictionary_path = DICTS_PATH / dic_name
    assert dictionary_path.is_file()

    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

    suggestions = sym_spell.lookup(input_term, Verbosity.CLOSEST, max_edit_distance=2)

    result = sym_spell.lookup_compound(input_phrase, max_edit_distance=2)

    ## Report
    print("=" * 50)
    print("Dictionary:", dic_name)

    print("Intput Term:", input_term)
    print("Suggestions:", [s.term for s in suggestions])

    print("Input Phrase:", input_phrase)
    print("Output (lookup Compound):", [s.term for s in result])


def main():
    input_term = "བཀྲ་ཤས་"
    input_phrase = "ཀ་་པག་ང་། བཀྲ་ཤས་བདེ་ལགས"
    dict_names = ["dictionary_bo_107_064.txt", "tc.txt", "gmd.txt"]

    for dict_name in dict_names:
        test_dictionary(dict_name, input_term, input_phrase)


if __name__ == "__main__":
    main()
