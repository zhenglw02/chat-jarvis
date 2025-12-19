import json
import os
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union

from config import system_config
from modules.brain.brain_interface import ChatItem

SelfAwakeSchedulerInstance = None

def init_scheduler(logger, jarvis):
    global SelfAwakeSchedulerInstance
    SelfAwakeSchedulerInstance = SelfAwakeScheduler(logger, jarvis)
    SelfAwakeSchedulerInstance.start()
    
def get_scheduler():
    return SelfAwakeSchedulerInstance

@dataclass
class SelfAwakeTask:
    
    def __init__(self, task_id: str, trigger_time: datetime, topic: str, prompt: str):
        self.task_id = task_id
        self.trigger_time = trigger_time
        self.topic = topic
        self.prompt = prompt

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class SelfAwakeScheduler:

    def __init__(self, logger, jarvis):
        self._logger = logger
        self._jarvis = jarvis
        self._tasks: List[SelfAwakeTask] = []
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        
        self._load_tasks()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop_with_restart, daemon=True, name="SelfAwakeLoop")
        self._thread.start()
        if self._logger:
            self._logger.info("self awake loop started")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def add_task(self, trigger_time: datetime, topic: str, prompt: str) -> str:
        task_id = uuid.uuid4().hex
        task = SelfAwakeTask(
            task_id=task_id,
            trigger_time=trigger_time,
            topic=topic,
            prompt=prompt,
        )
        with self._lock:
            self._tasks.append(task)
            self._tasks.sort(key=lambda item: item.trigger_time)
            self._persist_tasks()
        if self._logger:
            self._logger.info("add self awake task %s", task)
        return task_id

    def list_tasks(self) -> List[Dict[str, str]]:
        with self._lock:
            return [task.to_dict() for task in self._tasks]

    def remove_task(self, task_id: str) -> bool:
        removed = False
        with self._lock:
            new_tasks = [task for task in self._tasks if task.task_id != task_id]
            if len(new_tasks) != len(self._tasks):
                removed = True
                self._tasks = new_tasks
                self._persist_tasks()
        if removed and self._logger:
            self._logger.info("remove self awake task %s", task_id)
        return removed

    # ---------------- internal helpers ----------------

    def _loop_with_restart(self):
        while not self._stop_event.is_set():
            try:
                self._run_loop()
            except Exception as exc:  # pylint: disable=broad-except
                if self._logger:
                    self._logger.exception("self awake loop crashed, restarting", exc_info=exc)
                time.sleep(system_config.SELF_AWAKE_RESTART_DELAY)

    def _run_loop(self):
        while not self._stop_event.is_set():
            task = self._get_due_task()
            if task is None:
                time.sleep(system_config.SELF_AWAKE_CHECK_INTERVAL)
                continue
            self._execute_task(task)

    def _get_due_task(self) -> Optional[SelfAwakeTask]:
        with self._lock:
            if not self._tasks:
                return None
            now = datetime.now()
            first = self._tasks[0]
            if first.trigger_time <= now:
                task = self._tasks.pop(0)
                self._persist_tasks()
                return task
            return None

    def _execute_task(self, task: SelfAwakeTask):
        if self._logger:
            self._logger.info("trigger self awake task %s", task.task_id)
        if not self._jarvis:
            return
        content = (
            f"这是贾维斯的自我唤醒提醒。\n"
            f"计划事项：{task.topic}\n"
            f"计划时间：{task.trigger_time}\n"
            f"初始提示词：\n{task.prompt}\n"
            "请基于提示立即开始工作。"
        )
        chat_item = ChatItem.new("user", content)
        try:
            self._jarvis.handle_self_awake_request(chat_item)
        except AttributeError:
            self._jarvis.brain.handle_request(chat_item, self._jarvis.handle_brain_result)
        except Exception as exc:  # pylint: disable=broad-except
            if self._logger:
                self._logger.exception("self awake task execution failed", exc_info=exc)

    def _load_tasks(self):
        path = system_config.SELF_AWAKE_TASK_DATA_FILE
        if not os.path.exists(path):
            self._tasks = []
            return
        try:
            with open(path, "r", encoding="utf-8") as read_file:
                data = json.load(read_file)
        except (json.JSONDecodeError, OSError) as exc:
            self._tasks = []
            if self._logger:
                self._logger.warning("load self awake tasks failed: %s", exc)
            return
        self._tasks = [SelfAwakeTask(**item) for item in data]
        self._tasks.sort(key=lambda item: item.trigger_time)

    def _persist_tasks(self):
        path = system_config.SELF_AWAKE_TASK_DATA_FILE
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as write_file:
            json.dump([task.to_dict() for task in self._tasks], write_file, ensure_ascii=False, indent=2)
