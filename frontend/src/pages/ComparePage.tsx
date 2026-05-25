import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useCompareStore } from "@/stores/compareStore";
import { manufacturerService } from "@/api/client";
import type { Manufacturer } from "@/types/manufacturer";
import { useEffect, useState } from "react";

const categoryLabels: Record<string, string> = {
  turning: "车削",
  milling: "铣削",
  hole_making: "孔加工",
  threading: "螺纹",
  gear_cutting: "齿轮",
};

const geoLabelMap: Record<string, string> = {
  diameter: "直径", length: "总长", flute_length: "有效长",
  number_of_flutes: "刃数", helix_angle: "螺旋角", corner_radius: "刀尖R",
};

const paramLabelMap: Record<string, string> = {
  vc_steel: "Vc(钢)", vc_stainless: "Vc(不锈钢)", vc_cast_iron: "Vc(铸铁)",
  vc_aluminum: "Vc(铝)", vc_hardened: "Vc(硬材)", fn_steel: "fn(钢)",
  fn_stainless: "fn(不锈钢)", fn_cast_iron: "fn(铸铁)", fn_aluminum: "fn(铝)",
  fz_steel: "fz(钢)", fz_stainless: "fz(不锈钢)", fz_cast_iron: "fz(铸铁)",
  fz_aluminum: "fz(铝)", fz_hardened: "fz(硬材)",
  ap_max: "ap_max", ae_max: "ae_max", point_angle: "顶角",
  tolerance_class: "公差等级", bore_diameter_min: "最小孔径",
  bore_diameter_max: "最大孔径", adjustment_precision: "调节精度",
  module: "模数", pressure_angle: "压力角", number_of_starts: "头数",
  cooling_method: "冷却方式", max_l_d_ratio: "最大L/D比",
  surface_finish_ra: "表面粗糙度Ra(μm)", tolerance_grade: "公差等级(IT)",
};

const coolingMethodLabels: Record<number, string> = {
  0: "干切削", 1: "MQL微量润滑", 2: "浇注冷却", 3: "中心出水",
};

export default function ComparePage() {
  const navigate = useNavigate();
  const { items, removeItem, clearAll } = useCompareStore();
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);

  useEffect(() => {
    manufacturerService.list().then(setManufacturers);
  }, []);

  const getMfrName = (id?: string) => {
    if (!id) return "-";
    return manufacturers.find((m) => m.id === id)?.name_zh ?? id;
  };

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-16 text-center">
        <h2 className="mb-2 text-xl font-semibold">厂商对比</h2>
        <p className="mb-6 text-muted-foreground">
          在分类浏览页中添加刀具到对比列表
        </p>
        <Button onClick={() => navigate("/catalog")}>前往浏览</Button>
      </div>
    );
  }

  // Collect all unique param keys across items
  const allParamKeys = [...new Set(items.flatMap((c) => Object.keys(c.recommended_parameters)))];
  const allGeoKeys = [...new Set(items.flatMap((c) => Object.keys(c.geometry)))];

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-semibold">刀具对比</h2>
        <Button variant="outline" size="sm" onClick={clearAll}>
          清空对比
        </Button>
      </div>

      {/* Compare Cards */}
      <div className="mb-8 grid gap-4" style={{ gridTemplateColumns: `repeat(${items.length}, 1fr)` }}>
        {items.map((cutter) => (
          <Card key={cutter.id}>
            <CardHeader className="pb-2">
              <img
                src={cutter.image_url || "/images/cutters/placeholder.svg"}
                alt={cutter.name}
                className="mb-2 h-24 w-full rounded-md border object-cover"
              />
              <CardTitle className="text-sm leading-tight">{cutter.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 pt-0">
              <p className="text-xs text-muted-foreground">{cutter.model_number}</p>
              <p className="text-xs text-muted-foreground">{getMfrName(cutter.manufacturer_id)}</p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="secondary">
                  {categoryLabels[cutter.cutter_type.category] ?? cutter.cutter_type.category}
                </Badge>
                {cutter.cutter_type.variant && (
                  <Badge variant="outline">{cutter.cutter_type.variant}</Badge>
                )}
              </div>
              <div className="flex gap-1.5">
                <Button size="sm" variant="outline" onClick={() => navigate(`/cutter/${cutter.id}`)}>
                  详情
                </Button>
                <Button size="sm" variant="destructive" onClick={() => removeItem(cutter.id)}>
                  移除
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Geometry Table */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">几何参数对比</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="py-2 pr-4 text-left text-muted-foreground font-medium">参数</th>
                {items.map((c) => (
                  <th key={c.id} className="py-2 px-2 text-left font-medium truncate max-w-48">
                    {c.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {allGeoKeys.map((key) => (
                <tr key={key} className="border-b last:border-0">
                  <td className="py-2 pr-4 text-muted-foreground">
                    {geoLabelMap[key] ?? key}
                  </td>
                  {items.map((c) => {
                    const val = c.geometry[key as keyof typeof c.geometry];
                    return (
                      <td key={c.id} className="py-2 px-2 font-mono">
                        {val ?? "-"}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Parameters Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">切削参数对比</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="py-2 pr-4 text-left text-muted-foreground font-medium">参数</th>
                {items.map((c) => (
                  <th key={c.id} className="py-2 px-2 text-left font-medium truncate max-w-48">
                    {c.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {allParamKeys.map((key) => (
                <tr key={key} className="border-b last:border-0">
                  <td className="py-2 pr-4 text-muted-foreground">
                    {paramLabelMap[key] ?? key}
                  </td>
                  {items.map((c) => {
                    const val = c.recommended_parameters[key];
                    const display = key === "cooling_method" && val != null
                      ? (coolingMethodLabels[val as number] ?? String(val))
                      : (val ?? "-");
                    return (
                      <td key={c.id} className="py-2 px-2 font-mono">
                        {display}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
