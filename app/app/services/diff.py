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

    def __get_type(self, char):
        b = BoString(char)
        return b.get_categories()[0]

    def __handle_no_width_char(self, diffs):
        """attach no-width char to previous char.

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
        no_width_chars_types = [
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
        diffs = list(diffs)
        for i in range(len(diffs)):
            op, chunk = diffs[i]
            if len(chunk) == 1:
                if self.__get_type(chunk) in no_width_chars_types:
                    pre_op, pre_chunk = diffs[i - 1]

                    # add previous chunk's last char to current chunk
                    chunk = pre_chunk[-1] + chunk
                    diffs[i] = (op, chunk)

                    # remove last char from previous chunk
                    diffs[i - 1] = (pre_op, pre_chunk[:-1])

        return diffs

    def compute(self):
        diffs = get_diffs(self.text1, self.text2)
        diffs = self.__handle_no_width_char(diffs)
        return diffs
