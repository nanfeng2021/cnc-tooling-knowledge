"""
Cutter CQRS Handlers 单元测试

测试命令和查询处理器的业务逻辑，使用 Mock 仓库。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.application.commands.create_cutter import CreateCutterCommand
from src.application.commands.update_cutter import UpdateCutterCommand
from src.application.commands.delete_cutter import DeleteCutterCommand
from src.application.handlers.cutter_handler import CutterCommandHandler, CutterQueryHandler
from src.application.queries.cutter_queries import GetCutterByIdQuery, ListCuttersQuery, FilterCuttersQuery
from src.domain.models.cutter_aggregate import Cutter, CutterType, MaterialSpec, GeometryParams
from src.domain.repositories.cutter_repo import CutterNotFoundError


class TestCutterCommandHandler:
    """CutterCommandHandler 测试"""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """模拟刀具仓库"""
        repo = AsyncMock()
        repo.add = AsyncMock()
        repo.get_by_id = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock(return_value=True)
        return repo

    @pytest.fixture
    def mock_event_publisher(self) -> AsyncMock:
        """模拟事件发布者"""
        publisher = AsyncMock()
        publisher.publish = AsyncMock()
        return publisher

    @pytest.fixture
    def handler(self, mock_repository, mock_event_publisher) -> CutterCommandHandler:
        """创建命令处理器实例"""
        return CutterCommandHandler(
            repository=mock_repository,
            event_publisher=mock_event_publisher
        )

    @pytest.fixture
    def sample_cutter(self) -> Cutter:
        """创建示例刀具"""
        return Cutter.create(
            name="Test End Mill",
            cutter_type=CutterType(category="milling", subcategory="milling_end_mill", variant="square"),
            material=MaterialSpec(substrate="carbide_K20", coating_type="TiAlN"),
            geometry=GeometryParams(
                diameter=10.0,
                length=75.0,
                flute_length=30.0,
                number_of_flutes=4
            ),
            compatible_materials=["P", "K"]
        )

    @pytest.mark.asyncio
    async def test_handle_create_success(self, handler, mock_repository, mock_event_publisher):
        """测试成功创建刀具"""
        command = CreateCutterCommand(
            name="New End Mill",
            category="milling",
            subcategory="milling_end_mill",
            variant="square",
            substrate="carbide",
            coating_type="TiAlN",
            diameter=10.0,
            length=75.0,
            flute_length=30.0,
            number_of_flutes=4,
            compatible_materials=["P", "K"]
        )

        result = await handler.handle_create(command)

        # 验证仓库调用
        mock_repository.add.assert_called_once()
        added_cutter = mock_repository.add.call_args[0][0]
        assert added_cutter.name == "New End Mill"
        assert added_cutter.cutter_type.category == "milling"

        # 验证事件发布
        mock_event_publisher.publish.assert_called_once()
        event = mock_event_publisher.publish.call_args[0][0]
        assert event.event_type == "cutter.created"

        # 验证返回结果
        assert result.name == "New End Mill"
        assert result.cutter_type.category == "milling"

    @pytest.mark.asyncio
    async def test_handle_create_validation_error(self, handler):
        """测试创建刀具时验证失败"""
        command = CreateCutterCommand(
            name="",  # 空名称应该失败
            category="milling",
            substrate="carbide",
            diameter=10.0,
            length=75.0,
            flute_length=30.0,
            number_of_flutes=4
        )

        with pytest.raises(ValueError, match="Validation failed"):
            await handler.handle_create(command)

    @pytest.mark.asyncio
    async def test_handle_update_success(self, handler, mock_repository, mock_event_publisher, sample_cutter):
        """测试成功更新刀具"""
        # 设置仓库返回现有刀具
        mock_repository.get_by_id.return_value = sample_cutter

        command = UpdateCutterCommand(
            cutter_id=sample_cutter.id,
            name="Updated End Mill",
            recommended_parameters={"vc_steel": 200.0}
        )

        result = await handler.handle_update(command)

        # 验证仓库调用
        mock_repository.get_by_id.assert_called_once_with(sample_cutter.id)
        mock_repository.update.assert_called_once()

        # 验证事件发布
        mock_event_publisher.publish.assert_called_once()
        event = mock_event_publisher.publish.call_args[0][0]
        assert event.event_type == "cutter.updated"

        # 验证返回结果
        assert result.name == "Updated End Mill"

    @pytest.mark.asyncio
    async def test_handle_update_not_found(self, handler, mock_repository):
        """测试更新不存在的刀具"""
        # 设置仓库返回 None
        mock_repository.get_by_id.return_value = None

        command = UpdateCutterCommand(
            cutter_id=uuid4(),
            name="Updated End Mill"
        )

        with pytest.raises(CutterNotFoundError):
            await handler.handle_update(command)

    @pytest.mark.asyncio
    async def test_handle_delete_success(self, handler, mock_repository, mock_event_publisher):
        """测试成功删除刀具"""
        cutter_id = uuid4()

        command = DeleteCutterCommand(cutter_id=cutter_id)

        result = await handler.handle_delete(command)

        # 验证仓库调用
        mock_repository.delete.assert_called_once_with(cutter_id)

        # 验证事件发布
        mock_event_publisher.publish.assert_called_once()
        event = mock_event_publisher.publish.call_args[0][0]
        assert event.event_type == "cutter.deleted"

        # 验证返回结果
        assert result is True

    @pytest.mark.asyncio
    async def test_handle_delete_not_found(self, handler, mock_repository, mock_event_publisher):
        """测试删除不存在的刀具"""
        # 设置仓库返回 False
        mock_repository.delete.return_value = False

        cutter_id = uuid4()
        command = DeleteCutterCommand(cutter_id=cutter_id)

        result = await handler.handle_delete(command)

        # 验证仓库调用
        mock_repository.delete.assert_called_once_with(cutter_id)

        # 验证事件未发布
        mock_event_publisher.publish.assert_not_called()

        # 验证返回结果
        assert result is False


class TestCutterQueryHandler:
    """CutterQueryHandler 测试"""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """模拟刀具仓库"""
        repo = AsyncMock()
        repo.get_by_id = AsyncMock()
        repo.get_all = AsyncMock()
        repo.count = AsyncMock(return_value=10)
        repo.get_filtered = AsyncMock()
        return repo

    @pytest.fixture
    def handler(self, mock_repository) -> CutterQueryHandler:
        """创建查询处理器实例"""
        return CutterQueryHandler(repository=mock_repository)

    @pytest.fixture
    def sample_cutter(self) -> Cutter:
        """创建示例刀具"""
        return Cutter.create(
            name="Test End Mill",
            cutter_type=CutterType(category="milling", subcategory="milling_end_mill", variant="square"),
            material=MaterialSpec(substrate="carbide_K20", coating_type="TiAlN"),
            geometry=GeometryParams(
                diameter=10.0,
                length=75.0,
                flute_length=30.0,
                number_of_flutes=4
            ),
            compatible_materials=["P", "K"]
        )

    @pytest.mark.asyncio
    async def test_handle_get_by_id_success(self, handler, mock_repository, sample_cutter):
        """测试根据ID获取刀具"""
        # 设置仓库返回刀具
        mock_repository.get_by_id.return_value = sample_cutter

        query = GetCutterByIdQuery(cutter_id=str(sample_cutter.id))

        result = await handler.handle_get_by_id(query)

        # 验证仓库调用
        mock_repository.get_by_id.assert_called_once_with(sample_cutter.id)

        # 验证返回结果
        assert result is not None
        assert result.name == "Test End Mill"
        assert result.id == str(sample_cutter.id)

    @pytest.mark.asyncio
    async def test_handle_get_by_id_not_found(self, handler, mock_repository):
        """测试获取不存在的刀具"""
        # 设置仓库返回 None
        mock_repository.get_by_id.return_value = None

        query = GetCutterByIdQuery(cutter_id=str(uuid4()))

        result = await handler.handle_get_by_id(query)

        # 验证返回 None
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_get_by_id_invalid_uuid(self, handler, mock_repository):
        """测试使用无效UUID获取刀具"""
        query = GetCutterByIdQuery(cutter_id="invalid-uuid")

        result = await handler.handle_get_by_id(query)

        # 验证仓库未调用
        mock_repository.get_by_id.assert_not_called()

        # 验证返回 None
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_list(self, handler, mock_repository, sample_cutter):
        """测试列出刀具"""
        # 设置仓库返回刀具列表
        mock_repository.get_all.return_value = [sample_cutter]

        query = ListCuttersQuery(limit=10, offset=0)

        result = await handler.handle_list(query)

        # 验证仓库调用
        mock_repository.get_all.assert_called_once_with(limit=10, offset=0)
        mock_repository.count.assert_called_once()

        # 验证返回结果
        assert len(result.items) == 1
        assert result.total == 10
        assert result.limit == 10
        assert result.offset == 0

    @pytest.mark.asyncio
    async def test_handle_filter(self, handler, mock_repository, sample_cutter):
        """测试按条件过滤刀具"""
        # 设置仓库返回过滤结果
        mock_repository.get_filtered.return_value = ([sample_cutter], 1)

        query = FilterCuttersQuery(
            category="milling",
            subcategory="milling_end_mill",
            limit=10,
            offset=0
        )

        result = await handler.handle_filter(query)

        # 验证仓库调用
        mock_repository.get_filtered.assert_called_once_with(
            category="milling",
            subcategory="milling_end_mill",
            variant=None,
            manufacturer_id=None,
            limit=10,
            offset=0
        )

        # 验证返回结果
        assert len(result.items) == 1
        assert result.total == 1
