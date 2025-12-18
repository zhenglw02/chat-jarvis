import logging
from jarvis.jarvis import Jarvis
import inspect
import pkgutil
import importlib
import plugin
from plugin.plugin_interface import AbstractPlugin
import abc
from config import system_config


def load(logger: logging.Logger):
    """
    加载贾维斯对象
    :param logger:
    :return:
    """
    jarvis = Jarvis()

    function_map = {}
    functions = []

    # 从plugin目录下加载所有可用插件
    clz_list = []
    for importer, name, ispkg in pkgutil.walk_packages(plugin.__path__, "%s." % plugin.__name__):
        if not ispkg:
            module = importlib.import_module(name)
            temp_list = [value for (_, value) in inspect.getmembers(module) if inspect.isclass(value)]
            clz_list.extend(temp_list)
    for clz in clz_list:
        if not inspect.isabstract(clz) and not clz == abc.ABCMeta and clz.__name__.endswith("Plugin") and isinstance(
                clz(), AbstractPlugin):
            obj = clz()
            if not obj.valid():
                continue
            obj.init(logger)
            function_map[obj.get_name()] = {"chinese_name": obj.get_chinese_name(), "function": obj.run}
            functions.append(
                {
                    "type": "function",
                    "function": {
                        "name": obj.get_name(),
                        "description": obj.get_description(),
                        "parameters": obj.get_parameters(),
                    },
                }
            )

    logger.info("function_map: {}\n".format(function_map))
    logger.info("functions: {}\n".format(functions))

    jarvis.init(logger, function_map)

    mouth_class = _get_class(system_config.MOUTH_CLASS)
    jarvis.mouth = mouth_class()
    jarvis.mouth.init(logger)

    ear_class = _get_class(system_config.EAR_CLASS)
    jarvis.ear = ear_class()
    jarvis.ear.init(logger)

    eye_class = _get_class(system_config.EYE_CLASS)
    jarvis.eye = eye_class()
    jarvis.eye.init(logger)

    long_memory_class = _get_class(system_config.LONG_MEMORY_CLASS)
    jarvis.long_memory = long_memory_class()
    jarvis.long_memory.init(logger)

    short_memory_class = _get_class(system_config.SHORT_MEMORY_CLASS)
    jarvis.memory = short_memory_class()
    jarvis.memory.init(logger, jarvis.long_memory)

    brain_class = _get_class(system_config.BRAIN_CLASS)
    jarvis.brain = brain_class()
    jarvis.brain.init(logger, functions, jarvis.memory)

    dashboard_class = _get_class(system_config.DASHBOARD_CLASS)
    jarvis.dashboard = dashboard_class()
    jarvis.dashboard.init(logger)

    return jarvis


def _get_class(class_path: str):
    module_name, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
