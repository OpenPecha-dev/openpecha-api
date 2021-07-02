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

    def __get_type(self, char):
        b = BoString(char)
        return b.get_categories()[0]

    def __is_sub_char(self, char):
        return self.__get_type(char) in self.sub_char_types

    def __get_last_mingshi(self, text):
        """Return last mingshi of text."""
        mighshi = ""
        for char in reversed(text):
            if self.__is_sub_char(char):
                mighshi += char
            else:
                mighshi += char
                break

        return "".join(reversed(mighshi))

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
                pre_op, pre_chunk = diffs[i - 1]

                # add previous chunk's last mingshi to current chunk
                pre_chunk_last_mingshi = self.__get_last_mingshi(pre_chunk)
                chunk = pre_chunk_last_mingshi + chunk
                diffs[i] = (op, chunk)

                # remove last mingshi from previous chunk
                diffs[i - 1] = (pre_op, pre_chunk[: -len(pre_chunk_last_mingshi)])

        return diffs

    def compute(self):
        diffs = get_diffs(self.text1, self.text2)
        diffs = self.__handle_sub_char(diffs)
        return diffs
