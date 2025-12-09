from functools import wraps
import logging

from core.preprocessor import Preprocessor
from core.prediction_facade import PredictionFacade

logger = logging.getLogger(__name__)


def ensure_returns_str(func):
    """
    MOP Monitor for Preprocessor.clean:
    Ensures that the function always returns a string.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if not isinstance(result, str):
            msg = (
                f"[MOP] Violation: {func.__qualname__} "
                f"must return a string, but returned {type(result)}."
            )
            logger.error(msg)
            raise AssertionError(msg)

        return result

    return wrapper


def ensure_valid_prediction(func):
    """
    MOP Monitor for PredictionFacade.analyze:
    Ensures that:
      - The function returns a dictionary
      - The dictionary contains 'probability_machine' and 'label'
      - probability_machine is in the interval [0, 1]
      - label ∈ {'machine', 'human'}
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if not isinstance(result, dict):
            msg = (
                f"[MOP] Violation: {func.__qualname__} "
                f"must return a dictionary, but returned {type(result)}."
            )
            logger.error(msg)
            raise AssertionError(msg)

        if "probability_machine" not in result or "label" not in result:
            msg = (
                f"[MOP] Violation: {func.__qualname__} must contain "
                f"the keys 'probability_machine' and 'label', but returned: {result.keys()}."
            )
            logger.error(msg)
            raise AssertionError(msg)

        p = result["probability_machine"]
        label = result["label"]

        if not isinstance(p, (int, float)) or not (0.0 <= p <= 1.0):
            msg = (
                f"[MOP] Violation: probability_machine must be within [0, 1], "
                f"but is {p!r}."
            )
            logger.error(msg)
            raise AssertionError(msg)

        if label not in ("machine", "human"):
            msg = (
                f"[MOP] Violation: label must be either 'machine' or 'human', "
                f"but is {label!r}."
            )
            logger.error(msg)
            raise AssertionError(msg)

        print("[MOP] ensure_valid_prediction has passed!")

        return result

    return wrapper


# Instrumentation (monkey-patching)
Preprocessor.clean = ensure_returns_str(Preprocessor.clean)
PredictionFacade.analyze = ensure_valid_prediction(PredictionFacade.analyze)

logger.info(
    "[MOP] Component 1 active: Preprocessor.clean and PredictionFacade.analyze are monitored."
)
