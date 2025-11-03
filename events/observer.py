from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ProgressObserver(ABC):
    @abstractmethod
    def update(self, subject: ProgressSubject, payload: Dict[str, Any]) -> None: ...


class ProgressSubject(ABC):
    @abstractmethod
    def attach(self, observer: ProgressObserver) -> None: ...
    @abstractmethod
    def detach(self, observer: ProgressObserver) -> None: ...
    @abstractmethod
    def notify(self, payload: Dict[str, Any]) -> None: ...

class ConsoleProgressObserver(ProgressObserver):
    def update(self, subject: ProgressSubject, payload: Dict[str, Any]) -> None: ...

class LogProgressObserver(ProgressObserver):
    def update(self, subject: ProgressSubject, payload: Dict[str, Any]) -> None: ...
