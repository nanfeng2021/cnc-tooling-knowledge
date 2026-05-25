"""
G-code Generation Routes

G代码生成API端点。
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class GCodeRequest(BaseModel):
    """G代码生成请求"""
    cutter_id: str = Field(..., description="刀具ID")
    operation: str = Field(..., description="加工类型（milling/turning等）")
    workpiece_material: str = Field(..., description="工件材料")
    diameter: Optional[float] = Field(default=None, gt=0, description="刀具直径mm")
    width: Optional[float] = Field(default=None, gt=0, description="切削宽度mm")
    length: Optional[float] = Field(default=None, gt=0, description="切削长度mm")
    depth: Optional[float] = Field(default=None, gt=0, description="切削深度mm")


class GCodeSuggestion(BaseModel):
    """G代码建议"""
    operation: str
    gcode_lines: list[str]
    gcode_text: str
    description: str
    spindle_rpm: int
    feed_rate: float
    parameters_used: dict[str, Any] = {}
    warnings: list[str] = []


@router.post("/generate", response_model=GCodeSuggestion)
async def generate_gcode(request: GCodeRequest):
    """生成G代码建议"""
    try:
        # 根据材料和操作类型生成默认参数
        material_params = {
            "steel": {"vc": 180, "fz": 0.05, "ap": 2.0, "ae": 10.0},
            "stainless": {"vc": 120, "fz": 0.04, "ap": 1.5, "ae": 8.0},
            "cast_iron": {"vc": 200, "fz": 0.06, "ap": 2.5, "ae": 12.0},
            "aluminum": {"vc": 300, "fz": 0.08, "ap": 3.0, "ae": 15.0},
            "superalloy": {"vc": 60, "fz": 0.03, "ap": 1.0, "ae": 6.0},
            "hardened": {"vc": 80, "fz": 0.03, "ap": 0.5, "ae": 4.0},
        }

        # 材料代码映射
        material_map = {
            "P": "steel",
            "M": "stainless",
            "K": "cast_iron",
            "N": "aluminum",
            "S": "superalloy",
            "H": "hardened",
        }

        material_key = material_map.get(request.workpiece_material.upper(), request.workpiece_material.lower())
        params = material_params.get(material_key, material_params["steel"])

        # 计算主轴转速和进给速度
        diameter = request.diameter or 10.0
        vc = params["vc"]
        spindle_rpm = int((vc * 1000) / (3.14159 * diameter))

        if request.operation == "milling":
            fz = params["fz"]
            feed_rate = fz * 4 * spindle_rpm  # 假设4刃
        else:
            fn = params["fz"] * 2  # 车削进给量
            feed_rate = fn * spindle_rpm

        # 生成G代码
        depth = request.depth or params["ap"]
        width = request.width or params["ae"]
        length = request.length or 50.0

        gcode_lines = [
            "%",
            f"O1000 ({request.operation.upper()})",
            "G90 G21",
            f"S{spindle_rpm} M3",
            "G0 X0 Y0",
            f"G1 Z-{depth:.1f} F500",
            f"G1 X{length:.1f} F{feed_rate:.0f}",
            "G0 Z50.0",
            "M5",
            "M30",
            "%",
        ]

        warnings = []
        if vc > 250:
            warnings.append("切削速度较高，请确保刀具涂层适合")
        if depth > params["ap"] * 1.5:
            warnings.append("切削深度较大，建议分层切削")

        return GCodeSuggestion(
            operation=request.operation,
            gcode_lines=gcode_lines,
            gcode_text="\n".join(gcode_lines),
            description=f"{request.operation} operation for {request.workpiece_material}",
            spindle_rpm=spindle_rpm,
            feed_rate=feed_rate,
            parameters_used={
                "vc": vc,
                "fz": params["fz"],
                "spindle_rpm": spindle_rpm,
                "feed_rate": feed_rate,
            },
            warnings=warnings,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
