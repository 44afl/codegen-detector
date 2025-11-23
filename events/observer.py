from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import time


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

    def notify(self, payload: Dict[str, Any]) -> None:
        for obs in self._observers:
            obs.update(self, payload)

# Concrete Observers

class ConsoleProgressObserver(ProgressObserver):
    """Displays progress in the console: useful when running  training."""

    def update(self, subject: ProgressSubject, payload: Dict[str, Any]) -> None:
        ts = time.strftime("%H:%M:%S")
        msg = f"[{ts}] EVENT = {payload.get('event', 'unknown')}"
        for k, v in payload.items():
            if k != "event":
                msg += f" | {k} = {v}"
        print(msg)


class LogProgressObserver(ProgressObserver):
    """Writes progress to a JSONL file (one line = one event)."""

    def __init__(self, logfile: str = "training_progress.jsonl") -> None:
        self.logfile = logfile

    def update(self, subject: ProgressSubject, payload: Dict[str, Any]) -> None:
        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
