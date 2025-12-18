from __future__ import annotations

import importlib
import logging
from typing import Optional, Type

from config import system_config
from recorder.recorder_interface import RecorderInterface

_recorder_instance: Optional[RecorderInterface] = None
_recorder_class: Optional[Type[RecorderInterface]] = None


def _load_recorder_class() -> Type[RecorderInterface]:
    module_name, class_name = system_config.RECORDER_CLASS.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def init_recorder(logger: logging.Logger) -> RecorderInterface:
    """
    初始化 recorder 单例。
    """
    global _recorder_instance, _recorder_class
    if _recorder_instance is not None:
        return _recorder_instance

    _recorder_class = _load_recorder_class()
    if hasattr(_recorder_class, "get_recorder"):
        _recorder_instance = _recorder_class.get_recorder(
            system_config.RECORDER_STORAGE_DIR, logger
        )
    else:
        _recorder_instance = _recorder_class(
            system_config.RECORDER_STORAGE_DIR, logger
        )
    return _recorder_instance


def get_recorder() -> RecorderInterface:
    """
    获取 recorder 单例，未初始化时抛出异常。
    """
    if _recorder_instance is None:
        raise RuntimeError("Recorder has not been initialized yet.")
    return _recorder_instance
