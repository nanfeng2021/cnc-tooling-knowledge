"""
Recommendation Domain Service

参考原recommendation_service.py，实现切削参数推荐逻辑。
"""

from src.recommendation.domain.models.recommendation import ParameterRange, RecommendationResult

# ISO材料映射
_MATERIAL_ALIASES: dict[str, str] = {
    "P": "P", "M": "M", "K": "K", "N": "N", "S": "S", "H": "H",
    "steel": "P", "stainless": "M", "stainless_steel": "M",
    "cast_iron": "K", "aluminum": "N", "non_ferrous": "N",
    "superalloy": "S", "hardened": "H", "hard_material": "H",
}

_ISO_TO_KEY_SUFFIX: dict[str, str] = {
    "P": "steel", "M": "stainless", "K": "cast_iron",
    "N": "aluminum", "S": "superalloy", "H": "hardened",
}

_OPERATION_CONFIG: dict[str, tuple[str, bool]] = {
    "milling": ("fz", True),
    "turning": ("fn", False),
    "hole_making": ("fn", False),
    "threading": ("fn", False),
    "gear_cutting": ("fn", False),
}

_PARAM_UNITS: dict[str, str] = {
    "vc": "m/min", "fz": "mm/tooth", "fn": "mm/rev", "ap": "mm", "ae": "mm",
}


class RecommendationService:
    """切削参数推荐服务"""

    def __init__(self, vector_repo) -> None:
        self._vector_repo = vector_repo

    async def recommend(
        self,
        workpiece_material: str,
        operation_type: str,
        target_diameter: float | None = None,
        max_results: int = 5,
    ) -> RecommendationResult:
        """生成切削参数推荐"""
        # 解析ISO代码
        iso_code = self._resolve_iso_code(workpiece_material)

        # 搜索相关刀具文档
        query = f"{operation_type} cutter for {workpiece_material}"
        if target_diameter:
            query += f" diameter {target_diameter}mm"

        search_results = await self._vector_repo.search(
            query_text=query,
            top_k=max_results * 2,
            filters={"category": operation_type} if operation_type else None,
        )

        # 提取参数
        parameters: dict[str, list[float]] = {}
        source_docs = []

        for result in search_results:
            meta = result.metadata or {}
            params = meta.get("recommended_parameters", {})
            if isinstance(params, str):
                import json
                try:
                    params = json.loads(params)
                except:
                    params = {}

            if params:
                for key, value in params.items():
                    if isinstance(value, (int, float)):
                        if key not in parameters:
                            parameters[key] = []
                        parameters[key].append(float(value))

            source_docs.append({
                "document_id": result.document_id,
                "similarity": result.similarity_score,
                "metadata": meta,
            })

        # 聚合参数范围
        aggregated = {}
        suffix = _ISO_TO_KEY_SUFFIX.get(iso_code, iso_code.lower())
        expected_keys = self._get_expected_keys(operation_type, iso_code)

        for key in expected_keys:
            if key in parameters and parameters[key]:
                values = parameters[key]
                unit = ""
                for prefix, u in _PARAM_UNITS.items():
                    if key.startswith(prefix):
                        unit = u
                        break
                aggregated[key] = ParameterRange(
                    min_value=min(values),
                    max_value=max(values),
                    avg_value=sum(values) / len(values),
                    unit=unit,
                )

        return RecommendationResult(
            workpiece_material=workpiece_material,
            iso_code=iso_code,
            operation_type=operation_type,
            parameters=aggregated,
            source_documents=source_docs[:max_results],
            target_diameter=target_diameter,
        )

    def _resolve_iso_code(self, workpiece_material: str) -> str:
        """解析材料ISO代码"""
        normalized = workpiece_material.strip().lower()
        upper = normalized.upper()
        if upper in _MATERIAL_ALIASES:
            return _MATERIAL_ALIASES[upper]
        if normalized in _MATERIAL_ALIASES:
            return _MATERIAL_ALIASES[normalized]
        raise ValueError(f"Unknown workpiece material: {workpiece_material!r}")

    def _get_expected_keys(self, operation_type: str, iso_code: str) -> set[str]:
        """获取期望的参数键"""
        suffix = _ISO_TO_KEY_SUFFIX.get(iso_code, iso_code.lower())
        feed_prefix, include_ae = _OPERATION_CONFIG.get(operation_type.lower(), ("fz", True))
        keys = {f"vc_{suffix}", f"{feed_prefix}_{suffix}", "ap_max"}
        if include_ae:
            keys.add("ae_max")
        return keys
