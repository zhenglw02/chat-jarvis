from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol


@dataclass
class RecordItem:
    """结构化的记录数据."""

    source: str
    type: str
    data: Dict[str, Any] = field(default_factory=dict)


class RecorderInterface(Protocol):
    """记录器接口定义."""

    def __init__(self, storage_dir: str, logger: Optional[Any] = None) -> None:
        """初始化记录器."""
        ...

    def record(self, item: RecordItem) -> None:
        """记录一条数据."""
        ...

    @staticmethod
    def get_recorder() -> "RecorderInterface":
        """获取全局 recorder 实例."""
        ...
