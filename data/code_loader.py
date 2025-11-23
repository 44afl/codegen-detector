from abc import ABC, abstractmethod

# Factory Method
class CodeLoader(ABC):
    @abstractmethod
    def load(self, source):
        pass
    
class FileCodeLoader(CodeLoader):
    def load(self, source):
        pass
    
class TextInputCodeLoader(CodeLoader):
    def load(self, source):
        pass
    
class URLCodeLoader(CodeLoader):
    def load(self, source):
        pass