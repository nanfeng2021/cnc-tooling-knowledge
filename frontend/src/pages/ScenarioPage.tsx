import { useState, useEffect } from "react";
import { useScenarioStore } from "@/stores/scenarioStore";
import { categoryService } from "@/api/client";
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
import type { CategoryTree } from "@/types/category";

const MATERIALS = [
  { code: "P", label: "钢 (P)" },
  { code: "M", label: "不锈钢 (M)" },
  { code: "K", label: "铸铁 (K)" },
  { code: "N", label: "非铁金属 (N)" },
  { code: "S", label: "高温合金 (S)" },
  { code: "H", label: "硬材 (H)" },
];

const DIM_LABELS: Record<string, string> = {
  category: "类别",
  material: "材料",
  subcategory: "子类别",
  variant: "变体",
  diameter: "直径",
  parameters: "参数",
};

export default function ScenarioPage() {
  const [categories, setCategories] = useState<CategoryTree[]>([]);
  const [category, setCategory] = useState("milling");
  const [subcategory, setSubcategory] = useState("");
  const [variant, setVariant] = useState("");
  const [materialCode, setMaterialCode] = useState("P");
  const [diameter, setDiameter] = useState("");

  const { results, total, loading, error, matchScenario, reset } = useScenarioStore();

  useEffect(() => {
    categoryService.list().then(setCategories);
  }, []);

  const currentCat = categories.find((c) => c.id === category || c.category === category);
  const subcategories = currentCat?.subcategories ?? [];
  const currentSub = subcategories.find((s) => s.id === subcategory || s.subcategory === subcategory);
  const variants = currentSub?.variants ?? [];

  const handleMatch = () => {
    matchScenario({
      category,
      material_iso_code: materialCode,
      subcategory: subcategory || undefined,
      variant: variant || undefined,
      target_diameter: diameter ? parseFloat(diameter) : undefined,
      top_k: 10,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">场景选型匹配</h1>
        <p className="text-muted-foreground">根据加工场景描述，智能匹配最佳刀具</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>加工场景</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            <div className="space-y-1">
              <label className="text-sm font-medium">主类别</label>
              <Select value={category} onValueChange={(v) => { setCategory(v); setSubcategory(""); setVariant(""); }}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {categories.map((c) => (
                    <SelectItem key={c.id} value={c.id}>{c.label_zh}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">子类别</label>
              <Select value={subcategory} onValueChange={(v) => { setSubcategory(v); setVariant(""); }}>
                <SelectTrigger><SelectValue placeholder="全部" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="__all__">全部</SelectItem>
                  {subcategories.map((s) => (
                    <SelectItem key={s.id} value={s.id}>{s.label_zh}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">变体</label>
              <Select value={variant} onValueChange={setVariant}>
                <SelectTrigger><SelectValue placeholder="全部" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="__all__">全部</SelectItem>
                  {variants.map((v) => (
                    <SelectItem key={v.id} value={v.id}>{v.label_zh}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">工件材料</label>
              <Select value={materialCode} onValueChange={setMaterialCode}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {MATERIALS.map((m) => (
                    <SelectItem key={m.code} value={m.code}>{m.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium">目标直径 (mm)</label>
              <Input type="number" placeholder="可选" value={diameter} onChange={(e) => setDiameter(e.target.value)} min={0} />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <Button onClick={handleMatch} disabled={loading}>
              {loading ? "匹配中..." : "查找匹配刀具"}
            </Button>
            {results.length > 0 && <Button variant="outline" onClick={reset}>清除</Button>}
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6 text-destructive">{error}</CardContent>
        </Card>
      )}

      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              匹配结果
              <Badge variant="secondary">{total} 把刀具</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.map((r) => (
                <div key={r.cutter.id} className="rounded-lg border p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium">{r.cutter.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {r.cutter.cutter_type.category} / {r.cutter.cutter_type.subcategory} / {r.cutter.cutter_type.variant ?? "-"}
                        {" | "}
                        {r.cutter.geometry.diameter}mm
                        {r.cutter.manufacturer_id && ` | ${r.cutter.manufacturer_id}`}
                      </p>
                    </div>
                    <Badge className="text-base font-bold">
                      {(r.score * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {Object.entries(r.score_breakdown).map(([dim, val]) => (
                      <Badge
                        key={dim}
                        variant={val >= 0.8 ? "default" : val >= 0.4 ? "secondary" : "outline"}
                        className="text-xs"
                      >
                        {DIM_LABELS[dim] ?? dim}: {(val * 100).toFixed(0)}%
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
