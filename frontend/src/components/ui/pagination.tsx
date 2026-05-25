import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface PaginationProps {
  total: number;
  pageSize: number;
  currentPage: number; // 0-based
  onPageChange: (page: number) => void;
  siblingCount?: number;
}

function getPageRange(current: number, total: number, sibling: number): (number | "dots")[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i);
  }
  const pages: (number | "dots")[] = [0];
  const left = Math.max(1, current - sibling);
  const right = Math.min(total - 2, current + sibling);

  if (left > 1) pages.push("dots");
  for (let i = left; i <= right; i++) pages.push(i);
  if (right < total - 2) pages.push("dots");
  pages.push(total - 1);
  return pages;
}

export function Pagination({ total, pageSize, currentPage, onPageChange, siblingCount = 1 }: PaginationProps) {
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return null;

  const pages = getPageRange(currentPage, totalPages, siblingCount);
  const start = currentPage * pageSize + 1;
  const end = Math.min((currentPage + 1) * pageSize, total);

  return (
    <div className="flex items-center justify-between py-4">
      <p className="text-sm text-muted-foreground">
        共 {total} 条，当前第 {start}–{end} 条
      </p>
      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage === 0}
          onClick={() => onPageChange(currentPage - 1)}
        >
          上一页
        </Button>
        {pages.map((p, i) =>
          p === "dots" ? (
            <span key={`dots-${i}`} className="px-1 text-muted-foreground">
              ...
            </span>
          ) : (
            <Button
              key={p}
              variant={p === currentPage ? "default" : "ghost"}
              size="sm"
              className={cn("h-8 w-8 p-0")}
              onClick={() => onPageChange(p)}
            >
              {p + 1}
            </Button>
          )
        )}
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage >= totalPages - 1}
          onClick={() => onPageChange(currentPage + 1)}
        >
          下一页
        </Button>
      </div>
    </div>
  );
}
