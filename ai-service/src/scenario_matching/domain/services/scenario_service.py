"""
Scenario Matching Domain Service

参考原scenario_matching_service.py，实现场景匹配逻辑。
使用加权多标准评分：类别、材料兼容性、子类别、变体、直径适合度。
"""

import math

from src.scenario_matching.domain.models.machining_scenario import (
    MachiningScenario,
    ScenarioMatchResult,
)

# ISO代码映射
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

DEFAULT_WEIGHTS: dict[str, float] = {
    "category": 0.30,
    "material": 0.25,
    "subcategory": 0.15,
    "variant": 0.10,
    "diameter": 0.10,
    "parameters": 0.10,
}


class ScenarioMatchingService:
    """场景匹配服务"""

    def __init__(self, vector_repo, weights: dict[str, float] | None = None) -> None:
        self._vector_repo = vector_repo
        self._weights = weights or DEFAULT_WEIGHTS

    async def find_matches(
        self,
        scenario: MachiningScenario,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[ScenarioMatchResult]:
        """查找最佳匹配的刀具"""
        # 先用语义搜索获取候选
        query = f"{scenario.category} cutter for {scenario.material_iso_code}"
        if scenario.subcategory:
            query += f" {scenario.subcategory}"
        if scenario.variant:
            query += f" {scenario.variant}"

        search_results = await self._vector_repo.search(
            query_text=query,
            top_k=top_k * 3,  # 多取一些用于重排序
        )

        # 计算每个候选的匹配分数
        expected_keys = self._get_expected_param_keys(scenario.category, scenario.material_iso_code)
        results: list[ScenarioMatchResult] = []

        for result in search_results:
            meta = result.metadata or {}
            score, breakdown = self._compute_score(meta, scenario, expected_keys)

            if score >= min_score:
                results.append(ScenarioMatchResult(
                    document_id=result.document_id,
                    score=score,
                    score_breakdown=breakdown,
                    metadata=meta,
                ))

        # 按分数降序排序
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def _compute_score(
        self,
        metadata: dict,
        scenario: MachiningScenario,
        expected_keys: set[str],
    ) -> tuple[float, dict[str, float]]:
        """计算加权匹配分数"""
        breakdown = {
            "category": self._score_category(metadata, scenario.category),
            "material": self._score_material(metadata, scenario.material_iso_code),
            "subcategory": self._score_subcategory(metadata, scenario.subcategory),
            "variant": self._score_variant(metadata, scenario.variant),
            "diameter": self._score_diameter(metadata, scenario.target_diameter),
            "parameters": self._score_parameter_availability(metadata, expected_keys),
        }
        total = sum(self._weights[k] * v for k, v in breakdown.items())
        return round(total, 4), {k: round(v, 4) for k, v in breakdown.items()}

    def _score_category(self, metadata: dict, category: str) -> float:
        meta_category = metadata.get("category", "")
        return 1.0 if meta_category == category else 0.0

    def _score_material(self, metadata: dict, iso_code: str) -> float:
        compatible = metadata.get("compatible_materials", [])
        if isinstance(compatible, str):
            import json
            try:
                compatible = json.loads(compatible)
            except:
                compatible = []
        return 1.0 if iso_code in compatible else 0.0

    def _score_subcategory(self, metadata: dict, subcategory: str | None) -> float:
        if subcategory is None:
            return 0.5
        return 1.0 if metadata.get("subcategory", "") == subcategory else 0.0

    def _score_variant(self, metadata: dict, variant: str | None) -> float:
        if variant is None:
            return 0.5
        return 1.0 if metadata.get("variant", "") == variant else 0.0

    def _score_diameter(self, metadata: dict, target: float | None) -> float:
        if target is None or target <= 0:
            return 0.5
        diameter = metadata.get("diameter", 0)
        if isinstance(diameter, str):
            try:
                diameter = float(diameter)
            except:
                return 0.0
        if diameter <= 0:
            return 0.0
        sigma = 0.3 * target
        return math.exp(-(((diameter - target) / sigma) ** 2))

    def _score_parameter_availability(self, metadata: dict, expected_keys: set[str]) -> float:
        if not expected_keys:
            return 1.0
        params = metadata.get("recommended_parameters", {})
        if isinstance(params, str):
            import json
            try:
                params = json.loads(params)
            except:
                params = {}
        present = sum(1 for k in expected_keys if k in params)
        return present / len(expected_keys) if expected_keys else 1.0

    def _get_expected_param_keys(self, category: str, iso_code: str) -> set[str]:
        """获取期望的参数键"""
        suffix = _ISO_TO_KEY_SUFFIX.get(iso_code, iso_code.lower())
        feed_prefix, include_ae = _OPERATION_CONFIG.get(category.lower(), ("fz", True))
        keys = {f"vc_{suffix}", f"{feed_prefix}_{suffix}", "ap_max"}
        if include_ae:
            keys.add("ae_max")
        return keys
