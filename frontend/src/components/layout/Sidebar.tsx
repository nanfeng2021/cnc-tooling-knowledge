import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import type { CategoryTree } from "@/types/category";
import { categoryService } from "@/api/client";
import { useEffect, useState } from "react";

const categoryIcons: Record<string, string> = {
  turning: "车削",
  milling: "铣削",
  hole_making: "孔加工",
  threading: "螺纹",
  gear_cutting: "齿轮",
};

export function Sidebar() {
  const location = useLocation();
  const [categories, setCategories] = useState<CategoryTree[]>([]);

  useEffect(() => {
    categoryService.list().then(setCategories).catch(() => setCategories([]));
  }, []);

  return (
    <aside className="hidden w-56 shrink-0 border-r bg-muted/30 md:block">
      <div className="p-4">
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          刀具分类
        </h3>
        <nav className="space-y-1">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/catalog?category=${cat.id}`}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                location.search.includes(`category=${cat.id}`)
                  ? "bg-accent text-accent-foreground font-medium"
                  : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
              )}
            >
              <span className="text-xs">{categoryIcons[cat.id] ?? cat.id}</span>
              <span className="truncate">{cat.label_zh}</span>
              <span className="ml-auto text-xs text-muted-foreground">
                {cat.subcategories.length}
              </span>
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  );
}
