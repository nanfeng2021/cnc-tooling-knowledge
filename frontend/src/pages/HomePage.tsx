import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSearchStore } from "@/stores/searchStore";
import { useState } from "react";
import { Input } from "@/components/ui/input";

const categorySummary = [
  { id: "turning", label: "车削刀具", desc: "外圆/内孔/切槽/螺纹车削", count: "6子类 · 20变型" },
  { id: "milling", label: "铣削刀具", desc: "方肩/球头/高进给/面铣", count: "8子类 · 21变型" },
  { id: "hole_making", label: "孔加工刀具", desc: "钻/铰/镗/锪全工序", count: "4子类 · 18变型" },
  { id: "threading", label: "螺纹加工刀具", desc: "丝锥/板牙/螺纹铣/车", count: "4子类 · 13变型" },
  { id: "gear_cutting", label: "齿轮加工刀具", desc: "滚刀/插齿刀/剃齿刀", count: "5子类 · 12变型" },
];

export default function HomePage() {
  const navigate = useNavigate();
  const { search } = useSearchStore();
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (query.trim()) {
      search(query);
      navigate(`/search?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      {/* Hero */}
      <div className="mb-12 text-center">
        <h1 className="mb-3 text-3xl font-bold tracking-tight">
          CNC 刀具知识库
        </h1>
        <p className="mb-8 text-muted-foreground">
          数控刀具分类 · 应用场景 · 切削参数 · 厂商选型
        </p>

        {/* Search */}
        <div className="mx-auto flex max-w-xl gap-2">
          <Input
            placeholder="搜索刀具名称、型号、材料..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            className="h-11"
          />
          <Button onClick={handleSearch} className="h-11 px-6">
            搜索
          </Button>
        </div>
      </div>

      {/* Category Cards */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">刀具分类</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categorySummary.map((cat) => (
            <Card
              key={cat.id}
              className="cursor-pointer transition-shadow hover:shadow-md"
              onClick={() => navigate(`/catalog?category=${cat.id}`)}
            >
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{cat.label}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{cat.desc}</p>
                <p className="mt-2 text-xs text-muted-foreground">{cat.count}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Quick Links */}
      <div className="mt-10 flex gap-4">
        <Button variant="outline" onClick={() => navigate("/catalog")}>
          浏览全部分类
        </Button>
        <Button variant="outline" onClick={() => navigate("/compare")}>
          厂商对比
        </Button>
      </div>
    </div>
  );
}
