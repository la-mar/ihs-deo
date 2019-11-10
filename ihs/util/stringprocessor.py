import re


class StringProcessor(str):
    re_ws = re.compile(r"\s+")
    re_dup_ws = re.compile(r"\s\s+")
    re_non_alphanum = re.compile(r"(?ui)\W")
    replacement = "_"
    tolower = True

    def __init__(
        self, replacement: str = "_", tolower: bool = True, toupper: bool = False
    ):

        self.replacement = replacement
        self.tolower = tolower
        self.toupper = toupper

    def alphanum_only(self, s: str) -> str:
        """ force replacement using space so whitespace can be deduped later
        """

        return self.re_non_alphanum.sub(" ", s)

    def dedupe_whitespace(self, s: str) -> str:
        """ remove duplicated whitespaces
        """
        return self.re_dup_ws.sub(" ", s)

    def remove_whitespace(self, s: str) -> str:
        """ remove all whitespaces
        """
        return self.re_ws.sub("", s)

    def fill_whitespace(self, s: str, replacement: str = None) -> str:
        return s.replace(" ", replacement or self.replacement)

    def normalize(self, s: str, as_int: bool = False) -> str:
        """Normalizes the given string. Operations performed on the string are:
                - remove all non-alphanumeric characters
                - squish sequential whitespace to a single space
                - convert to all lower case
                - strip leading and trailing whitespace

        Arguments:
            string {str} -- a string to process

        Keyword Arguments:
            replacement {str} -- replacement for regex substitutions (default: {''})

        Returns:
            str -- the normalized string
        """

        if s is not None:
            s = str(s)
            s = self.alphanum_only(s)
            s = self.dedupe_whitespace(s)
            s = str.strip(s)

            if as_int:
                s = self.remove_whitespace(s)
                # dont actually convert to int to avoid the potential failure point during ingestion
            else:
                s = self.fill_whitespace(s)

                if self.toupper:
                    s = s.upper()
                elif self.tolower:
                    s = s.lower()

        return s


if __name__ == "__main__":

    sp = StringProcessor()

    sp.normalize("  test               TEST   Test     ") == "test_test_test"

    sp.normalize("1,232", as_int=True) == str(1232)

    sp.normalize(None) is None
