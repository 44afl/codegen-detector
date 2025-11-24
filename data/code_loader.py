# Factory Method

from abc import ABC, abstractmethod
from aop.aspects import log_call, timeit, debug

class CodeLoader(ABC):
    @abstractmethod
    def load(self, source):
        pass
    
    @staticmethod
    def create(source_type: str):
        if source_type == "file":
            return FileCodeLoader()
        elif source_type == "text":
            return TextInputCodeLoader()
        else:
            raise ValueError("Invalid source type")
 
@timeit 
@log_call          
class FileCodeLoader(CodeLoader):
    def load(self, source):
        with open(source, "r", encoding="utf-8") as f:
            return f.read()

@timeit 
@log_call
class TextInputCodeLoader(CodeLoader):
    def load(self, source):
        return source