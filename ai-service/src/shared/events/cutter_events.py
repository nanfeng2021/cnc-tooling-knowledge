"""
Shared Cutter Events

与cutter-management共享的事件定义。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class CutterEvent:
    """刀具事件基类"""

    event_id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    cutter_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CutterEvent":
        """从字典反序列化"""
        event_type = data.get("event_type", "")
        if event_type == "cutter.created":
            return CutterCreatedEvent(
                event_id=UUID(data["event_id"]),
                cutter_id=data["cutter_id"],
                name=data.get("name", ""),
                category=data.get("category", ""),
                subcategory=data.get("subcategory", ""),
            )
        elif event_type == "cutter.updated":
            return CutterUpdatedEvent(
                event_id=UUID(data["event_id"]),
                cutter_id=data["cutter_id"],
                name=data.get("name", ""),
                category=data.get("category", ""),
            )
        elif event_type == "cutter.deleted":
            return CutterDeletedEvent(
                event_id=UUID(data["event_id"]),
                cutter_id=data["cutter_id"],
            )
        return cls(event_id=UUID(data.get("event_id", str(uuid4()))), event_type=event_type)


@dataclass(frozen=True)
class CutterCreatedEvent(CutterEvent):
    """刀具创建事件"""
    event_type: str = "cutter.created"
    name: str = ""
    category: str = ""
    subcategory: str = ""


@dataclass(frozen=True)
class CutterUpdatedEvent(CutterEvent):
    """刀具更新事件"""
    event_type: str = "cutter.updated"
    name: str = ""
    category: str = ""


@dataclass(frozen=True)
class CutterDeletedEvent(CutterEvent):
    """刀具删除事件"""
    event_type: str = "cutter.deleted"
