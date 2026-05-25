import { useState, useEffect } from "react";
import { useGCodeStore } from "@/stores/gcodeStore";
import { cutterService } from "@/api/client";
import type { Cutter } from "@/types/cutter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const OPERATIONS = [
  { value: "facing", label: "面铣 (Facing)" },
  { value: "contouring", label: "轮廓铣 (Contouring)" },
  { value: "pocketing", label: "型腔铣 (Pocketing)" },
  { value: "od_turning", label: "外圆车削 (OD Turning)" },
  { value: "drilling", label: "钻孔 (Drilling)" },
  { value: "peck_drilling", label: "啄钻 (Peck Drilling)" },
];

const MATERIALS = [
  { value: "steel", label: "钢 (P)" },
  { value: "stainless", label: "不锈钢 (M)" },
  { value: "cast_iron", label: "铸铁 (K)" },
  { value: "aluminum", label: "铝合金 (N)" },
  { value: "superalloy", label: "高温合金 (S)" },
];

export default function GCodePage() {
  const [cutters, setCutters] = useState<Cutter[]>([]);
  const [cutterId, setCutterId] = useState("");
  const [operation, setOperation] = useState("facing");
  const [material, setMaterial] = useState("steel");
  const [width, setWidth] = useState("");
  const [length, setLength] = useState("");
  const [depth, setDepth] = useState("");

  const { result, loading, error, generate, reset } = useGCodeStore();

  useEffect(() => {
    cutterService.list({ limit: 100 }).then((res) => setCutters(res.items));
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cutterId) return;
    generate({
      cutterId,
      operation,
      workpieceMaterial: material,
      width: width ? parseFloat(width) : undefined,
      length: length ? parseFloat(length) : undefined,
      depth: depth ? parseFloat(depth) : undefined,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">G代码辅助</h1>
        <p className="text-muted-foreground">选择刀具和加工参数，自动生成G代码建议</p>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">刀具</label>
          <select
            value={cutterId}
            onChange={(e) => setCutterId(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">选择刀具...</option>
            {cutters.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} (D{c.geometry.diameter}mm)
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">加工类型</label>
          <select
            value={operation}
            onChange={(e) => setOperation(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            {OPERATIONS.map((op) => (
              <option key={op.value} value={op.value}>
                {op.label}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">工件材料</label>
          <select
            value={material}
            onChange={(e) => setMaterial(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            {MATERIALS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">切深 (mm)</label>
          <Input
            type="number"
            step="0.5"
            placeholder="可选"
            value={depth}
            onChange={(e) => setDepth(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">宽度 (mm)</label>
          <Input
            type="number"
            step="1"
            placeholder="可选"
            value={width}
            onChange={(e) => setWidth(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">长度 (mm)</label>
          <Input
            type="number"
            step="1"
            placeholder="可选"
            value={length}
            onChange={(e) => setLength(e.target.value)}
          />
        </div>

        <div className="md:col-span-2 flex gap-2">
          <Button type="submit" disabled={loading || !cutterId}>
            {loading ? "生成中..." : "生成 G代码"}
          </Button>
          {result && (
            <Button variant="outline" onClick={reset}>
              清除
            </Button>
          )}
        </div>
      </form>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6 text-destructive">{error}</CardContent>
        </Card>
      )}

      {result && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {result.description}
                <Badge>{result.operation}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center p-2 rounded bg-muted">
                  <p className="text-xs text-muted-foreground">主轴转速</p>
                  <p className="font-bold">{result.spindle_rpm} RPM</p>
                </div>
                <div className="text-center p-2 rounded bg-muted">
                  <p className="text-xs text-muted-foreground">进给速度</p>
                  <p className="font-bold">{result.feed_rate} mm/min</p>
                </div>
                {Object.entries(result.parameters_used)
                  .filter(([k]) => !["spindle_rpm", "feed_rate"].includes(k))
                  .map(([k, v]) => (
                    <div key={k} className="text-center p-2 rounded bg-muted">
                      <p className="text-xs text-muted-foreground">{k}</p>
                      <p className="font-bold">{v}</p>
                    </div>
                  ))}
              </div>

              {result.warnings.length > 0 && (
                <div className="mb-4 p-3 rounded bg-yellow-50 border border-yellow-200 text-yellow-800 text-sm">
                  {result.warnings.map((w, i) => (
                    <p key={i}>{w}</p>
                  ))}
                </div>
              )}

              <pre className="bg-slate-900 text-green-400 p-4 rounded-lg text-xs overflow-x-auto font-mono">
                {result.gcode_lines.join("\n")}
              </pre>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
