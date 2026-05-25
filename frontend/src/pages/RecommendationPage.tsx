import { useState } from "react";
import { useRecommendationStore } from "@/stores/recommendationStore";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";

const MATERIALS = [
  { code: "P", label: "钢 (P)" },
  { code: "M", label: "不锈钢 (M)" },
  { code: "K", label: "铸铁 (K)" },
  { code: "N", label: "非铁金属 (N)" },
  { code: "S", label: "高温合金 (S)" },
  { code: "H", label: "硬材 (H)" },
];

const OPERATIONS = [
  { value: "milling", label: "铣削" },
  { value: "turning", label: "车削" },
  { value: "hole_making", label: "孔加工" },
  { value: "threading", label: "螺纹加工" },
  { value: "gear_cutting", label: "齿轮加工" },
];

const PARAM_LABELS: Record<string, string> = {
  vc_steel: "切削速度 (钢)",
  vc_stainless: "切削速度 (不锈钢)",
  vc_cast_iron: "切削速度 (铸铁)",
  vc_aluminum: "切削速度 (铝)",
  vc_superalloy: "切削速度 (高温合金)",
  vc_hardened: "切削速度 (硬材)",
  fz_steel: "每齿进给 (钢)",
  fz_stainless: "每齿进给 (不锈钢)",
  fz_cast_iron: "每齿进给 (铸铁)",
  fz_aluminum: "每齿进给 (铝)",
  fn_steel: "每转进给 (钢)",
  fn_stainless: "每转进给 (不锈钢)",
  fn_cast_iron: "每转进给 (铸铁)",
  fn_aluminum: "每转进给 (铝)",
  ap_max: "最大切深",
  ae_max: "最大切宽",
};

export default function RecommendationPage() {
  const [material, setMaterial] = useState("P");
  const [operation, setOperation] = useState("milling");
  const [diameter, setDiameter] = useState("");
  const { result, loading, error, fetchParameters, reset } = useRecommendationStore();

  const handleSearch = () => {
    const d = diameter ? parseFloat(diameter) : undefined;
    fetchParameters(material, operation, d);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">切削参数推荐</h1>
        <p className="text-muted-foreground">根据工件材料和加工类型，推荐切削参数范围</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>加工条件</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">工件材料</label>
              <Select value={material} onValueChange={setMaterial}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {MATERIALS.map((m) => (
                    <SelectItem key={m.code} value={m.code}>
                      {m.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">加工类型</label>
              <Select value={operation} onValueChange={setOperation}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {OPERATIONS.map((o) => (
                    <SelectItem key={o.value} value={o.value}>
                      {o.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">目标直径 (mm)</label>
              <Input
                type="number"
                placeholder="可选"
                value={diameter}
                onChange={(e) => setDiameter(e.target.value)}
                min={0}
              />
            </div>
            <div className="flex items-end gap-2">
              <Button onClick={handleSearch} disabled={loading}>
                {loading ? "查询中..." : "获取推荐"}
              </Button>
              {result && (
                <Button variant="outline" onClick={reset}>
                  清除
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6 text-destructive">{error}</CardContent>
        </Card>
      )}

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                推荐参数
                <Badge variant="secondary">{result.candidate_count} 把刀具参考</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {Object.keys(result.parameters).length === 0 ? (
                <p className="text-muted-foreground">未找到匹配的切削参数数据</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="py-2 text-left font-medium">参数</th>
                        <th className="py-2 text-right font-medium">最小值</th>
                        <th className="py-2 text-right font-medium">平均值</th>
                        <th className="py-2 text-right font-medium">最大值</th>
                        <th className="py-2 text-right font-medium">单位</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(result.parameters).map(([key, range]) => (
                        <tr key={key} className="border-b last:border-0">
                          <td className="py-2">{PARAM_LABELS[key] ?? key}</td>
                          <td className="py-2 text-right font-mono">{range.min_value.toFixed(2)}</td>
                          <td className="py-2 text-right font-mono font-semibold">{range.avg_value.toFixed(2)}</td>
                          <td className="py-2 text-right font-mono">{range.max_value.toFixed(2)}</td>
                          <td className="py-2 text-right text-muted-foreground">{range.unit}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          {result.source_cutters.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>参考刀具</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {result.source_cutters.map((c) => (
                    <div key={c.id} className="rounded-lg border p-3">
                      <p className="font-medium">{c.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {c.cutter_type.category} / {c.cutter_type.variant ?? "-"} | {c.geometry.diameter}mm
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
