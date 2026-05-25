import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "首页", path: "/" },
  { label: "分类浏览", path: "/catalog" },
  { label: "参数推荐", path: "/recommend" },
  { label: "场景选型", path: "/scenario" },
  { label: "智能问答", path: "/qa" },
  { label: "G代码", path: "/gcode" },
  { label: "厂商对比", path: "/compare" },
];

export function Header() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center px-6">
        <Link to="/" className="mr-8 flex items-center gap-2 font-bold text-lg">
          <span className="text-primary">CNC</span>
          <span className="text-muted-foreground">刀具知识库</span>
        </Link>

        <nav className="flex items-center gap-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                location.pathname === item.path
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="ml-auto text-xs text-muted-foreground">
          数控刀具分类 · 应用 · 选型
        </div>
      </div>
    </header>
  );
}
