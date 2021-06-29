from app.services.diff import Diff


def test_vowels_diff():
    differ = Diff("བཀྲ་ཤིས།", "བཀ་ཤས།")

    diffs = differ.compute()

    assert diffs == [(0, "བ"), (-1, "ཀྲ"), (0, "་"), (-1, "ཤི"), (0, "ས།")]
