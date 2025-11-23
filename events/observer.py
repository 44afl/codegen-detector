from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json

import time
from aop.aspects import log_call, debug


#Observer interface

class ProgressObserver(ABC):
    """Abstract Observer for progress updates."""

    @abstractmethod
    def update(self, subject: "ProgressSubject", payload: Dict[str, Any]) -> None:
        pass

# Subject 

class ProgressSubject:
    """Concrete Subject (Trainer, Evaluator, etc.)."""

    def __init__(self) -> None:
        self._observers: List[ProgressObserver] = []

    def attach(self, observer: ProgressObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: ProgressObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    @log_call
    @debug
    def notify(self, payload: Dict[str, Any]) -> None:
        for obs in self._observers:
            obs.update(self, payload)

# Concrete Observers

class ConsoleProgressObserver(ProgressObserver):
    def update(self, subject: "ProgressSubject", payload: Dict[str, Any]) -> None:
        step = payload.get("step")
        prog = payload.get("progress")
        print(f"[OBS-CONSOLE] {step} -> {prog}%")


class LogProgressObserver(ProgressObserver):
    def __init__(self, path: str = "training_progress.log") -> None:
        self.path = path

    def update(self, subject: "ProgressSubject", payload: Dict[str, Any]) -> None:
        step = payload.get("step")
        prog = payload.get("progress")
        with open(self.path, "a") as f:
            f.write(f"{step},{prog}\n")
