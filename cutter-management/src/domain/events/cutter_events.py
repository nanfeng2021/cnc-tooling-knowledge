"""
Cutter Domain Events

定义刀具相关的领域事件，用于事件驱动的服务间通信。
事件通过RabbitMQ发布，ai-service消费后同步向量索引。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """领域事件基类"""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = field(init=False)

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典"""
        data = {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
        }
        for key, value in self.__dict__.items():
            if key not in ("event_id", "occurred_at", "event_type"):
                if isinstance(value, UUID):
                    data[key] = str(value)
                elif isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = value
        return data


@dataclass(frozen=True)
class CutterCreated(DomainEvent):
    """刀具创建事件"""

    cutter_id: UUID = UUID(int=0)
    name: str = ""
    category: str = ""
    subcategory: str = ""
    event_type: str = field(default="cutter.created", init=False)


@dataclass(frozen=True)
class CutterUpdated(DomainEvent):
    """刀具更新事件"""

    cutter_id: UUID = UUID(int=0)
    name: str = ""
    category: str = ""
    event_type: str = field(default="cutter.updated", init=False)


@dataclass(frozen=True)
class CutterDeleted(DomainEvent):
    """刀具删除事件"""

    cutter_id: UUID = UUID(int=0)
    event_type: str = field(default="cutter.deleted", init=False)
