import re

from antx.core import get_diffs
from botok import BoString


class Diff:
    """
    Diff class to finds diffs and make diffs presentable.

    Especially no-width characters, which can't be styled
    in HTML alone.

    Args:
        text1 (str): text to be diff
        text2 (str): text to be diff against by text1
    """

    def __init__(self, text1, text2):
        self.text1 = text1
        self.text2 = text2
        self.sub_char_types = [
            "SKRT_SUB_CONS",
            "VOW",
            "NFC",
            "SKRT_VOW",
            "IN_SYL_MARK",
            "IN_SYL_MARK",
            "KRT_LONG_VOW",
            "SKRT_SUB_CONS",
            "SUB_CONS",
            "IN_SYL_MARK",
        ]

    @staticmethod
    def __get_type(char):
        b = BoString(char)
        return b.get_categories()[0]

    def __is_sub_char(self, char):
        return self.__get_type(char) in self.sub_char_types

    def __is_dokchen(self, char):
        return self.__get_type(char) == "SUB_CONS" and char in ["ྲ", "ྱ", "ླ"]

    def __is_vowel(self, char):
        return self.__get_type(char) in ["VOW", "SKRT_VOW", "KRT_LONG_VOW"]

    def __get_last_mingshi(self, text, sub_char):
        """Return last main stack of text and whether to duplicate it or not

        Returns (tuple): (duplicate(bool), main_stack(str))
        """
        mighshi = ""
        duplicate = False
        for char in reversed(text):
            if self.__is_sub_char(char):
                mighshi += char
            else:
                mighshi += char
                break

        if not self.__is_vowel(sub_char) and self.__is_dokchen(mighshi[0]):
            mighshi = mighshi[1:]
            duplicate = True

        return duplicate, "".join(reversed(mighshi))

    def __handle_sub_char(self, diffs):
        """attach sub char to previous char.

        Examples no-width char from botok string categories:
            0F71,—ཱ—,SKRT_SUB_CONS
            0F72,—ི—,VOW
            0F73,—ཱི—,NFC
            0F76,—ྲྀ—,NFC
            0F7D,—ཽ—,SKRT_VOW
            0F7E,—ཾ—,IN_SYL_MARK
            0F35,—༵—,IN_SYL_MARK
            0F7F,——,SKRT_LONG_VOW
            0FAF,—ྯ—,SKRT_SUB_CONS
            0FB2,—ྲ—,SUB_CONS
            —༵—,IN_SYL_MARK
        """
        diffs = list(diffs)
        for i in range(len(diffs)):
            op, chunk = diffs[i]
            if self.__is_sub_char(chunk[0]):
                if op != 0:
                    pre_op, pre_chunk = diffs[i - 1]

                    # add previous chunk's last mingshi to current chunk
                    duplicate, pre_chunk_last_mingshi = self.__get_last_mingshi(
                        pre_chunk, chunk[0]
                    )
                    chunk = pre_chunk_last_mingshi + chunk
                    diffs[i] = (op, chunk)

                    # remove last mingshi from previous chunk
                    if not duplicate:
                        diffs[i - 1] = (
                            pre_op,
                            pre_chunk[: -len(pre_chunk_last_mingshi)],
                        )
                else:
                    # add vowels to previous diffs
                    reversed_i = i - 1
                    reversed_op, reversed_chunk = diffs[reversed_i]
                    while reversed_i >= 0 and reversed_op != 0:
                        diffs[reversed_i] = (reversed_op, reversed_chunk + chunk[0])
                        reversed_i -= 1
                        reversed_op, reversed_chunk = diffs[reversed_i]

                    diffs[i] = (op, chunk[1:])

        return diffs

    def compute(self):
        diffs = get_diffs(self.text1, self.text2)
        diffs = self.__handle_sub_char(diffs)
        return diffs
