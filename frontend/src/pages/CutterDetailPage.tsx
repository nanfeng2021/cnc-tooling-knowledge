import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cutterService, manufacturerService } from "@/api/client";
import { useCompareStore } from "@/stores/compareStore";
import type { Cutter } from "@/types/cutter";
import type { Manufacturer } from "@/types/manufacturer";

const categoryLabels: Record<string, string> = {
  turning: "车削",
  milling: "铣削",
  hole_making: "孔加工",
  threading: "螺纹",
  gear_cutting: "齿轮",
};

const coolingMethodLabels: Record<number, string> = {
  0: "干切削",
  1: "MQL微量润滑",
  2: "浇注冷却",
  3: "中心出水",
};

export default function CutterDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [cutter, setCutter] = useState<Cutter | null>(null);
  const [manufacturer, setManufacturer] = useState<Manufacturer | null>(null);
  const { addItem, isInCompare } = useCompareStore();

  useEffect(() => {
    if (!id) return;
    cutterService.getById(id).then((c) => {
      setCutter(c);
      if (c?.manufacturer_id) {
        manufacturerService.getById(c.manufacturer_id).then(setManufacturer);
      }
    });
  }, [id]);

  if (!cutter) {
    return <div className="p-6 text-muted-foreground">加载中...</div>;
  }

  const geoEntries = Object.entries(cutter.geometry)
    .filter(([, v]) => v !== 0 && v !== null)
    .map(([k, v]) => ({ key: k, value: v }));

  const paramEntries = Object.entries(cutter.recommended_parameters)
    .map(([k, v]) => ({ key: k, value: v }));

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

  const geoLabelMap: Record<string, string> = {
    diameter: "直径", length: "总长", flute_length: "有效长",
    number_of_flutes: "刃数/槽数", helix_angle: "螺旋角", corner_radius: "刀尖R",
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      {/* Back */}
      <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="mb-4">
        ← 返回
      </Button>

      {/* Header with hero image */}
      <div className="mb-6 flex gap-6">
        <img
          src={cutter.image_url || "/images/cutters/placeholder.svg"}
          alt={cutter.name}
          className="h-40 w-40 shrink-0 rounded-lg border object-cover"
        />
        <div>
          <h1 className="text-2xl font-bold">{cutter.name}</h1>
          <p className="text-muted-foreground">{cutter.model_number}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge>{categoryLabels[cutter.cutter_type.category] ?? cutter.cutter_type.category}</Badge>
            <Badge variant="outline">{cutter.cutter_type.subcategory}</Badge>
            {cutter.cutter_type.variant && (
              <Badge variant="outline">{cutter.cutter_type.variant}</Badge>
            )}
            {manufacturer && (
              <Badge variant="secondary">{manufacturer.name_zh}</Badge>
            )}
          </div>
        </div>
      </div>

      {/* Action */}
      <div className="mb-6">
        <Button
          variant={isInCompare(cutter.id) ? "destructive" : "default"}
          onClick={() => addItem(cutter)}
        >
          {isInCompare(cutter.id) ? "已加入对比" : "加入对比"}
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="geometry">
        <TabsList>
          <TabsTrigger value="geometry">几何参数</TabsTrigger>
          <TabsTrigger value="material">材料信息</TabsTrigger>
          <TabsTrigger value="parameters">切削参数</TabsTrigger>
          <TabsTrigger value="guidelines">使用指南</TabsTrigger>
        </TabsList>

        <TabsContent value="geometry">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">几何参数</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                {geoEntries.map(({ key, value }) => (
                  <div key={key} className="flex justify-between rounded-md bg-muted/50 px-3 py-2 text-sm">
                    <span className="text-muted-foreground">
                      {geoLabelMap[key] ?? key}
                    </span>
                    <span className="font-mono">{value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="material">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">材料信息</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                <div className="flex justify-between rounded-md bg-muted/50 px-3 py-2 text-sm">
                  <span className="text-muted-foreground">基体</span>
                  <span className="font-mono">{cutter.material.substrate}</span>
                </div>
                {cutter.material.coating_type && (
                  <div className="flex justify-between rounded-md bg-muted/50 px-3 py-2 text-sm">
                    <span className="text-muted-foreground">涂层</span>
                    <span className="font-mono">{cutter.material.coating_type}</span>
                  </div>
                )}
                {cutter.material.hardness_hrc && (
                  <div className="flex justify-between rounded-md bg-muted/50 px-3 py-2 text-sm">
                    <span className="text-muted-foreground">硬度(HRC)</span>
                    <span className="font-mono">{cutter.material.hardness_hrc}</span>
                  </div>
                )}
                {cutter.material.iso_class && (
                  <div className="flex justify-between rounded-md bg-muted/50 px-3 py-2 text-sm">
                    <span className="text-muted-foreground">ISO等级</span>
                    <span className="font-mono">{cutter.material.iso_class}</span>
                  </div>
                )}
              </div>
              <div className="mt-4">
                <p className="mb-2 text-sm text-muted-foreground">适用材料</p>
                <div className="flex gap-1.5">
                  {cutter.compatible_materials.map((m) => (
                    <Badge key={m} variant="secondary">{m}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="parameters">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">推荐切削参数</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                {paramEntries.map(({ key, value }) => (
                  <div key={key} className="flex justify-between rounded-md bg-muted/50 px-3 py-2 text-sm">
                    <span className="text-muted-foreground">
                      {paramLabelMap[key] ?? key}
                    </span>
                    <span className="font-mono">
                      {key === "cooling_method"
                        ? (coolingMethodLabels[value as number] ?? String(value))
                        : value}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="guidelines">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">使用指南</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {cutter.usage_guidelines.map((g, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                    {g}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
