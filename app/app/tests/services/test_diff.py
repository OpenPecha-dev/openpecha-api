import pytest

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


def test_bug_1():
    differ = Diff("བསྒྲུབས་", "བསྒྱུབས་")

    diffs = differ.compute()

    assert diffs == [(0, "བ"), (-1, "སྒྲ"), (1, "སྒྱ"), (0, "ུབས་")]


def test_bug_2():
    differ = Diff("སྲུལ", "སྲལ")

    diffs = differ.compute()

    assert diffs == [(0, ""), (-1, "སྲུ"), (0, "ལ")]


def test_bug_4():
    differ = Diff("སྟོད་", "སྤྱོད་")

    diffs = differ.compute()

    assert diffs == [(0, ""), (-1, "སྲུ"), (0, "ལ")]


@pytest.mark.skip()
def test_bug_3():
    differ = Diff("སྡོགས", "སྩོགས")

    diffs = differ.compute()

    assert diffs == [(0, ""), (-1, "སྲུ"), (0, "ལ")]
