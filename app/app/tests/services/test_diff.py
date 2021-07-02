from app.services.diff import Diff


def test_vowel_and_sub_cons():
    differ = Diff("བཀྲ་ཤིས།", "བཀ་ཤས།")

    diffs = differ.compute()

    assert diffs == [(0, "བ"), (-1, "ཀྲ"), (0, "་"), (-1, "ཤི"), (0, "ས།")]


def test_triplet_migshi_both_sub_missing():
    differ = Diff("སངས་རྒྱས་", "སངས་རས་")

    diffs = differ.compute()

    assert diffs == [(0, "སངས་"), (-1, "རྒྱ"), (0, "ས་")]


def test_triplet_mingshi_only_last_sub_missing():
    differ = Diff("སངས་རྒྱས་", "སངས་རྒས་")

    diffs = differ.compute()

    assert diffs == [(0, "སངས་"), (-1, "རྒྱ"), (0, "ས་")]
