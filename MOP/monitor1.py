from functools import wraps
import logging

from core.preprocessor import Preprocessor
from core.prediction_facade import PredictionFacade

logger = logging.getLogger(__name__)


def ensure_returns_str(func):
 
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if not isinstance(result, str):
            msg = (
                f"[MOP] Violation: {func.__qualname__} "
                f"trebuie să returneze str, dar a întors {type(result)}"
            )
            logger.error(msg)
            raise AssertionError(msg)

        return result

    return wrapper


def ensure_valid_prediction(func):
    """
    Monitor pentru PredictionFacade.analyze:
      - trebuie să întoarcă un dict
      - cu cheile: 'probability_machine' și 'label'
      - probability_machine ∈ [0, 1]
      - label ∈ {'machine', 'human'}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if not isinstance(result, dict):
            msg = (
                f"[MOP] Violation: {func.__qualname__} "
                f"trebuie să returneze dict, nu {type(result)}"
            )
            logger.error(msg)
            raise AssertionError(msg)

        if "probability_machine" not in result or "label" not in result:
            msg = (
                f"[MOP] Violation: {func.__qualname__} trebuie să conțină "
                f"cheile 'probability_machine' și 'label', dar a întors: {result.keys()}"
            )
            logger.error(msg)
            raise AssertionError(msg)

        p = result["probability_machine"]
        label = result["label"]

        if not isinstance(p, (int, float)) or not (0.0 <= p <= 1.0):
            msg = (
                f"[MOP] Violation: probability_machine trebuie să fie în [0, 1], "
                f"dar este {p!r}"
            )
            logger.error(msg)
            raise AssertionError(msg)

        if label not in ("machine", "human"):
            msg = (
                f"[MOP] Violation: label trebuie să fie 'machine' sau 'human', "
                f"dar este {label!r}"
            )
            logger.error(msg)
            raise AssertionError(msg)

        return result

    return wrapper


Preprocessor.clean = ensure_returns_str(Preprocessor.clean)
PredictionFacade.analyze = ensure_valid_prediction(PredictionFacade.analyze)

logger.info(
    "[MOP] Componenta 1 activă: Preprocessor.clean și PredictionFacade.analyze sunt monitorizate."
)
