"""
Manufacturer Aggregate

制造商聚合根。
"""

from uuid import UUID, uuid4


class Manufacturer:
    """制造商聚合根"""

    def __init__(
        self,
        name: str,
        country: str = "",
        website: str = "",
        id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        self.name = name
        self.country = country
        self.website = website

    def __repr__(self) -> str:
        return f"Manufacturer(id={self.id}, name={self.name!r})"
