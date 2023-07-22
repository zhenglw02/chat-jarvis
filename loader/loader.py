import logging
from jarvis.jarvis import Jarvis
import inspect
import pkgutil
import importlib
import plugin
from plugin.plugin_interface import AbstractPlugin
import abc
from modules.ear.baidu_ear import BaiduEar
from modules.mouth.baidu_mouth import BaiduMouth
from modules.brain.gpt35_brain import GPT35Brain
from modules.dashboard.simple_dashboard import SimpleDashboard
from modules.memory.memory_memory import MemoryMemory


def load(logger: logging.Logger):
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
            functions.append({
                "name": obj.get_name(),
                "description": obj.get_description(),
                "parameters": obj.get_parameters()
            })

    logger.info("function_map: {}\n".format(function_map))
    logger.info("functions: {}\n".format(functions))

    jarvis.init(logger, function_map)

    jarvis.mouth = BaiduMouth()
    jarvis.mouth.init(logger)

    jarvis.ear = BaiduEar()
    jarvis.ear.init(logger)

    jarvis.memory = MemoryMemory()
    jarvis.memory.init(logger)

    jarvis.brain = GPT35Brain()
    jarvis.brain.init(logger, functions, jarvis.memory)

    jarvis.dashboard = SimpleDashboard()
    jarvis.dashboard.init(logger)

    return jarvis
