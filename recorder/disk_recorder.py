from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar, Optional

from .recorder_interface import RecordItem, RecorderInterface

DEFAULT_MAX_FILE_SIZE = 1024**3  # 1GB


class DiskRecorder(RecorderInterface):
    """将记录数据持久化为 JSONL 文件，并在达到阈值时切分文件。"""

    _shared_instance: ClassVar[Optional["DiskRecorder"]] = None
    _instance_lock: ClassVar[Lock] = Lock()

    def __init__(
        self,
        storage_dir: str,
        logger: Optional[logging.Logger] = None,
        *,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        file_prefix: str = "records",
    ) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        self.max_file_size = max_file_size
        self.file_prefix = file_prefix
        self._lock = Lock()
        self._sequence = 0
        self._current_file_path, self._current_file_size = self._prepare_initial_file()
        if DiskRecorder._shared_instance is None:
            DiskRecorder._shared_instance = self

    @staticmethod
    def get_recorder(
        storage_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        *,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        file_prefix: str = "records",
    ) -> "DiskRecorder":
        """
        获取（或在必要时创建）全局 DiskRecorder 实例，确保运行期间固定使用同一个 recorder。
        """
        if DiskRecorder._shared_instance is not None:
            return DiskRecorder._shared_instance
        if storage_dir is None:
            raise ValueError(
                "storage_dir is required when the recorder has not been initialized."
            )
        with DiskRecorder._instance_lock:
            if DiskRecorder._shared_instance is None:
                DiskRecorder._shared_instance = DiskRecorder(
                    storage_dir,
                    logger,
                    max_file_size=max_file_size,
                    file_prefix=file_prefix,
                )
        return DiskRecorder._shared_instance

    def record(self, item: RecordItem) -> None:
        payload = {"source": item.source, "type": item.type, "data": item.data}
        line = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
        data_bytes = line.encode("utf-8")
        with self._lock:
            self._roll_file_if_needed(len(data_bytes))
            with open(self._current_file_path, "ab") as handler:
                handler.write(data_bytes)
            self._current_file_size += len(data_bytes)

    def _prepare_initial_file(self) -> tuple[Path, int]:
        files = sorted(self.storage_dir.glob(f"{self.file_prefix}_*.jsonl"))
        if files:
            latest = files[-1]
            self._sequence = self._extract_sequence(latest.name)
            size = latest.stat().st_size
            if size < self.max_file_size:
                return latest, size
            self._sequence += 1
            new_file = self._create_file(self._sequence)
            return new_file, 0
        new_file = self._create_file(self._sequence)
        return new_file, 0

    def _roll_file_if_needed(self, next_write_size: int) -> None:
        projected_size = self._current_file_size + next_write_size
        if projected_size <= self.max_file_size:
            return
        self._sequence += 1
        self._current_file_path = self._create_file(self._sequence)
        self._current_file_size = 0
        self.logger.debug(
            "DiskRecorder rolled file to %s", self._current_file_path.as_posix()
        )

    def _create_file(self, sequence: int) -> Path:
        file_path = self.storage_dir / f"{self.file_prefix}_{sequence:05d}.jsonl"
        file_path.touch(exist_ok=True)
        return file_path

    def _extract_sequence(self, filename: str) -> int:
        try:
            return int(filename.split("_")[-1].split(".")[0])
        except (ValueError, IndexError):
            self.logger.warning("Unexpected recorder filename pattern: %s", filename)
            return 0
