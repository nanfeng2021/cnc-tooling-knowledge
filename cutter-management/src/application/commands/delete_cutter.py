"""
Delete Cutter Command

删除刀具的CQRS命令。
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteCutterCommand:
    """删除刀具命令"""

    cutter_id: UUID
