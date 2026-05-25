"""
Cutter CQRS Handlers

命令和查询处理器，参考原src/application/handlers/cutter_handler.py迁移。
"""

from uuid import UUID

from src.application.commands.create_cutter import CreateCutterCommand
from src.application.commands.update_cutter import UpdateCutterCommand
from src.application.commands.delete_cutter import DeleteCutterCommand
from src.application.dto.cutter_dto import CutterDTO, CutterListResponse
from src.application.queries.cutter_queries import (
    FilterCuttersQuery,
    GetCutterByIdQuery,
    ListCuttersQuery,
)
from src.domain.models.cutter_aggregate import (
    Cutter,
    CutterType,
    GeometryParams,
    MaterialSpec,
)
from src.domain.repositories.cutter_repo import CutterNotFoundError, CutterRepository


class CutterCommandHandler:
    """刀具命令处理器"""

    def __init__(
        self,
        repository: CutterRepository,
        event_publisher=None,
    ) -> None:
        self._repository = repository
        self._event_publisher = event_publisher

    async def handle_create(self, command: CreateCutterCommand) -> CutterDTO:
        """处理创建刀具命令"""
        # 验证命令
        errors = command.validate()
        if errors:
            raise ValueError(f"Validation failed: {', '.join(errors)}")

        # 创建领域对象
        cutter = Cutter.create(
            name=command.name,
            cutter_type=CutterType(
                category=command.category,
                subcategory=command.subcategory,
                variant=command.variant,
            ),
            material=MaterialSpec(
                substrate=command.substrate,
                coating_type=command.coating_type,
                hardness_hrc=command.hardness_hrc,
                iso_class=command.iso_class,
                material_grade=command.material_grade,
            ),
            geometry=GeometryParams(
                diameter=command.diameter,
                length=command.length,
                flute_length=command.flute_length,
                number_of_flutes=command.number_of_flutes,
                helix_angle=command.helix_angle,
                corner_radius=command.corner_radius,
            ),
            manufacturer_id=command.manufacturer_id,
            model_number=command.model_number,
            image_url=command.image_url,
            recommended_parameters=command.recommended_parameters,
            usage_guidelines=command.usage_guidelines,
            compatible_materials=command.compatible_materials,
            cutter_id=command.cutter_id,
        )

        # 持久化
        await self._repository.add(cutter)

        # 发布领域事件
        if self._event_publisher:
            from src.domain.events.cutter_events import CutterCreated
            event = CutterCreated(
                cutter_id=cutter.id,
                name=cutter.name,
                category=cutter.cutter_type.category,
                subcategory=cutter.cutter_type.subcategory,
            )
            await self._event_publisher.publish(event)

        return CutterDTO.from_domain(cutter)

    async def handle_update(self, command: UpdateCutterCommand) -> CutterDTO:
        """处理更新刀具命令"""
        cutter = await self._repository.get_by_id(command.cutter_id)
        if not cutter:
            raise CutterNotFoundError(f"Cutter {command.cutter_id} not found")

        # 更新基本信息
        if command.name is not None:
            cutter.update_info(name=command.name)
        if command.model_number is not None:
            cutter.update_info(model_number=command.model_number)
        if command.image_url is not None:
            cutter.update_info(image_url=command.image_url)
        if command.usage_guidelines is not None:
            cutter.update_info(usage_guidelines=command.usage_guidelines)

        # 更新推荐参数
        if command.recommended_parameters:
            cutter.update_parameters(command.recommended_parameters)

        # 更新兼容材料
        if command.compatible_materials is not None:
            cutter.compatible_materials = command.compatible_materials
            cutter.updated_at = __import__("datetime").datetime.utcnow()

        # 持久化
        await self._repository.update(cutter)

        # 发布领域事件
        if self._event_publisher:
            from src.domain.events.cutter_events import CutterUpdated
            event = CutterUpdated(
                cutter_id=cutter.id,
                name=cutter.name,
                category=cutter.cutter_type.category,
            )
            await self._event_publisher.publish(event)

        return CutterDTO.from_domain(cutter)

    async def handle_delete(self, command: DeleteCutterCommand) -> bool:
        """处理删除刀具命令"""
        result = await self._repository.delete(command.cutter_id)

        # 发布领域事件
        if result and self._event_publisher:
            from src.domain.events.cutter_events import CutterDeleted
            event = CutterDeleted(cutter_id=command.cutter_id)
            await self._event_publisher.publish(event)

        return result


class CutterQueryHandler:
    """刀具查询处理器"""

    def __init__(self, repository: CutterRepository) -> None:
        self._repository = repository

    async def handle_get_by_id(self, query: GetCutterByIdQuery) -> CutterDTO | None:
        """根据ID获取刀具"""
        try:
            cutter_id = UUID(query.cutter_id)
        except ValueError:
            return None

        cutter = await self._repository.get_by_id(cutter_id)
        if not cutter:
            return None
        return CutterDTO.from_domain(cutter)

    async def handle_list(self, query: ListCuttersQuery) -> CutterListResponse:
        """列出刀具"""
        cutters = await self._repository.get_all(limit=query.limit, offset=query.offset)
        total = await self._repository.count()
        return CutterListResponse(
            items=[CutterDTO.from_domain(c) for c in cutters],
            total=total,
            limit=query.limit,
            offset=query.offset,
        )

    async def handle_filter(self, query: FilterCuttersQuery) -> CutterListResponse:
        """按条件过滤刀具"""
        manufacturer_id = None
        if query.manufacturer_id:
            try:
                manufacturer_id = UUID(query.manufacturer_id)
            except ValueError:
                pass

        cutters, total = await self._repository.get_filtered(
            category=query.category,
            subcategory=query.subcategory,
            variant=query.variant,
            manufacturer_id=manufacturer_id,
            limit=query.limit,
            offset=query.offset,
        )
        return CutterListResponse(
            items=[CutterDTO.from_domain(c) for c in cutters],
            total=total,
            limit=query.limit,
            offset=query.offset,
        )
