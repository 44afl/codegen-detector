import re

class Preprocessor:
    def __init__(self):
        pass

    def clean(self, code: str) -> str:
        if not isinstance(code, str):
            return ""

        code = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', code)

        code = code.replace("\r\n", "\n").replace("\r", "\n")

        code = "\n".join(line.rstrip() for line in code.split("\n"))

        code = re.sub(r'\t+', '\t', code)
        code = re.sub(r' {2,}', ' ', code)

        #return None. -pt testare monitor
        return code
