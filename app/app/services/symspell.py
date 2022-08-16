from ossaudiodev import SNDCTL_SYNTH_REMOVESAMPLE
from typing import List

from symspellpy import SymSpell, Verbosity

from app.core.config import settings


class SymSpellModel:
    """
    Candidate model based on symspell algorithm.
    https://github.com/wolfgarbe/SymSpell
    """

    def __init__(self,):
        self.sym_spell = SymSpell()
        self.load_dictionary()

    def load_dictionary(self):
        if not settings.SYMSPELL_DICTIONARY_PATH.is_file():
            raise FileNotFoundError("Dictionary doesn't exists")
        self.sym_spell.load_dictionary(
            settings.SYMSPELL_DICTIONARY_PATH, term_index=0, count_index=1
        )

    def get_candidates(self, word: str, n=float("inf")) -> List[str]:
        suggested_words = []

        suggestions = self.sym_spell.lookup(
            word, Verbosity.CLOSEST, max_edit_distance=2
        )
        for i, suggestion in enumerate(suggestions):
            if i > n:
                break
            suggested_words.append(suggestion.term)

        suggestions = self.sym_spell.lookup_compound(word, max_edit_distance=2)
        for suggestion in suggestions:
            suggested_words.append(suggestion.term)

        return suggested_words


symspell_lookup = SymSpellModel()
