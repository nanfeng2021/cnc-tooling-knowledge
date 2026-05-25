import { useSearchParams, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useSearchStore } from "@/stores/searchStore";
import { manufacturerService } from "@/api/client";
import type { Manufacturer } from "@/types/manufacturer";
import { useState } from "react";

export default function SearchPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { query, results, total, loading, search, setQuery } = useSearchStore();
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);

  useEffect(() => {
    manufacturerService.list().then(setManufacturers);
  }, []);

  useEffect(() => {
    const q = params.get("q") ?? "";
    if (q) {
      setQuery(q);
      search(q);
    }
  }, [params]);

  const handleSearch = () => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}`);
    }
  };

  const getMfrName = (id?: string) => {
    if (!id) return "-";
    return manufacturers.find((m) => m.id === id)?.name_zh ?? id;
  };

  const categoryLabels: Record<string, string> = {
    turning: "车削",
    milling: "铣削",
    hole_making: "孔加工",
    threading: "螺纹",
    gear_cutting: "齿轮",
  };

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      {/* Search Bar */}
      <div className="mb-6 flex gap-2">
        <Input
          placeholder="搜索刀具名称、型号、材料..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          className="h-10"
        />
        <Button onClick={handleSearch}>搜索</Button>
      </div>

      {/* Results */}
      {loading && <p className="text-muted-foreground">搜索中...</p>}

      {!loading && results.length > 0 && (
        <>
          <p className="mb-4 text-sm text-muted-foreground">
            找到 {total} 个结果
          </p>
          <div className="space-y-3">
            {results.map(({ cutter }) => (
              <Card
                key={cutter.id}
                className="cursor-pointer transition-shadow hover:shadow-md"
                onClick={() => navigate(`/cutter/${cutter.id}`)}
              >
                <CardContent className="flex items-center gap-4 p-4">
                  <img
                    src={cutter.image_url || "/images/cutters/placeholder.svg"}
                    alt={cutter.name}
                    className="h-12 w-12 shrink-0 rounded-md border object-cover"
                  />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium truncate">{cutter.name}</h3>
                    <p className="text-sm text-muted-foreground truncate">
                      {cutter.model_number}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge variant="secondary">
                      {categoryLabels[cutter.cutter_type.category] ?? cutter.cutter_type.category}
                    </Badge>
                    {cutter.cutter_type.variant && (
                      <Badge variant="outline">{cutter.cutter_type.variant}</Badge>
                    )}
                    <span className="text-xs text-muted-foreground">
                      {getMfrName(cutter.manufacturer_id)}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}

      {!loading && results.length === 0 && query && (
        <p className="text-center text-muted-foreground py-12">
          未找到与 "{query}" 相关的刀具
        </p>
      )}
    </div>
  );
}
