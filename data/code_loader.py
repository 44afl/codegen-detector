# Factory Method

from abc import ABC, abstractmethod

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
    
class FileCodeLoader(CodeLoader):
    def load(self, source):
        with open(source, "r", encoding="utf-8") as f:
            return f.read()
        
class TextInputCodeLoader(CodeLoader):
    def load(self, source):
        return source