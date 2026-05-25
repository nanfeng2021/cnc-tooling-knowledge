import { useSearchParams, useNavigate } from "react-router-dom";
import { useEffect, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Pagination } from "@/components/ui/pagination";
import { useCatalogStore } from "@/stores/catalogStore";
import { useCompareStore } from "@/stores/compareStore";
import { ISO_CLASSES } from "@/types/material";

const categoryLabels: Record<string, string> = {
  turning: "车削",
  milling: "铣削",
  hole_making: "孔加工",
  threading: "螺纹",
  gear_cutting: "齿轮",
};

export default function CatalogPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const {
    categories,
    manufacturers,
    cutters,
    total,
    loading,
    selectedCategory,
    selectedSubcategory,
    selectedVariant,
    selectedManufacturer,
    selectedIsoClass,
    page,
    pageSize,
    setCategory,
    setSubcategory,
    setVariant,
    setManufacturer,
    setIsoClass,
    setPage,
    resetFilters,
    fetchCategories,
    fetchCutters,
  } = useCatalogStore();

  const { addItem, removeItem, isInCompare } = useCompareStore();

  // 构建 URL 并导航
  const updateUrl = useCallback((overrides?: Record<string, string | null>) => {
    const next = new URLSearchParams();
    const cat = overrides?.category ?? selectedCategory;
    const sub = overrides?.subcategory ?? selectedSubcategory;
    const vrt = overrides?.variant ?? selectedVariant;
    const mfr = overrides?.manufacturer_id ?? selectedManufacturer;
    const iso = overrides?.iso_class ?? selectedIsoClass;
    const pg = overrides?.page ?? String(page + 1);

    if (cat) next.set("category", cat);
    if (sub) next.set("subcategory", sub);
    if (vrt) next.set("variant", vrt);
    if (mfr) next.set("manufacturer_id", mfr);
    if (iso) next.set("iso_class", iso);
    if (pg && pg !== "1") next.set("page", pg);

    const qs = next.toString();
    navigate(`/catalog${qs ? `?${qs}` : ""}`, { replace: true });
  }, [selectedCategory, selectedSubcategory, selectedVariant, selectedManufacturer, selectedIsoClass, page, navigate]);

  // 初始化：加载分类列表
  useEffect(() => {
    fetchCategories();
  }, []);

  // 从 URL 参数初始化 store
  useEffect(() => {
    const cat = params.get("category");
    const sub = params.get("subcategory");
    const vrt = params.get("variant");
    const mfr = params.get("manufacturer_id");
    const iso = params.get("iso_class");
    const pg = params.get("page");

    if (cat && cat !== selectedCategory) setCategory(cat);
    if (sub && sub !== selectedSubcategory) setSubcategory(sub);
    if (vrt && vrt !== selectedVariant) setVariant(vrt);
    if (mfr && mfr !== selectedManufacturer) setManufacturer(mfr);
    if (iso && iso !== selectedIsoClass) setIsoClass(iso);
    if (pg) {
      const p = parseInt(pg, 10);
      if (!isNaN(p) && p - 1 !== page) setPage(Math.max(0, p - 1));
    }
  }, []); // 仅初始化时执行

  // 筛选/分页变化时重新加载
  useEffect(() => {
    fetchCutters();
  }, [selectedCategory, selectedSubcategory, selectedVariant, selectedManufacturer, selectedIsoClass, page]);

  const currentCat = categories.find((c) => c.id === selectedCategory);
  const currentSub = currentCat?.subcategories.find((s) => s.id === selectedSubcategory);

  // 筛选操作 handlers
  const handleCategoryChange = (cat: string | null) => {
    setCategory(cat);
    updateUrl({ category: cat, subcategory: null, variant: null, page: "1" });
  };

  const handleSubcategoryChange = (sub: string | null) => {
    setSubcategory(sub);
    updateUrl({ subcategory: sub, variant: null, page: "1" });
  };

  const handleVariantChange = (v: string | null) => {
    setVariant(v);
    updateUrl({ variant: v, page: "1" });
  };

  const handleManufacturerChange = (val: string) => {
    const mfr = val === "__all__" ? null : val;
    setManufacturer(mfr);
    updateUrl({ manufacturer_id: mfr, page: "1" });
  };

  const handleIsoClassChange = (iso: string | null) => {
    setIsoClass(iso);
    updateUrl({ iso_class: iso, page: "1" });
  };

  const handlePageChange = (p: number) => {
    setPage(p);
    updateUrl({ page: String(p + 1) });
  };

  const handleReset = () => {
    resetFilters();
    navigate("/catalog", { replace: true });
  };

  const hasAnyFilter = selectedCategory || selectedSubcategory || selectedVariant || selectedManufacturer || selectedIsoClass;

  return (
    <div className="px-6 py-6">
      {/* ① 主分类 Tab */}
      <div className="mb-3 flex flex-wrap gap-2">
        <Button
          variant={!selectedCategory ? "default" : "outline"}
          size="sm"
          onClick={() => handleCategoryChange(null)}
        >
          全部
        </Button>
        {categories.map((cat) => (
          <Button
            key={cat.id}
            variant={selectedCategory === cat.id ? "default" : "outline"}
            size="sm"
            onClick={() => handleCategoryChange(cat.id)}
          >
            {cat.label_zh}
          </Button>
        ))}
      </div>

      {/* ② 子分类 */}
      {currentCat && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          <Button
            variant={!selectedSubcategory ? "secondary" : "ghost"}
            size="sm"
            onClick={() => handleSubcategoryChange(null)}
          >
            全部
          </Button>
          {currentCat.subcategories.map((sub) => (
            <Button
              key={sub.id}
              variant={selectedSubcategory === sub.id ? "secondary" : "ghost"}
              size="sm"
              onClick={() => handleSubcategoryChange(sub.id)}
            >
              {sub.label_zh}
            </Button>
          ))}
        </div>
      )}

      {/* ③ 筛选器区域 */}
      <div className="mb-4 space-y-2 rounded-md border bg-muted/30 p-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* 厂商下拉 */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground">厂商</span>
            <Select
              value={selectedManufacturer ?? "__all__"}
              onValueChange={handleManufacturerChange}
            >
              <SelectTrigger className="h-8 w-40">
                <SelectValue placeholder="全部厂商" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__all__">全部厂商</SelectItem>
                {Array.isArray(manufacturers) && manufacturers.map((mfr) => (
                  <SelectItem key={mfr.id} value={mfr.id}>
                    {mfr.name_zh}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* ISO 材料类别 */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-medium text-muted-foreground">材料</span>
            <Button
              variant={!selectedIsoClass ? "secondary" : "ghost"}
              size="sm"
              className="h-7 text-xs"
              onClick={() => handleIsoClassChange(null)}
            >
              全部
            </Button>
            {ISO_CLASSES.map((iso) => (
              <Button
                key={iso.code}
                variant={selectedIsoClass === iso.code ? "default" : "outline"}
                size="sm"
                className={`h-7 text-xs ${selectedIsoClass !== iso.code ? iso.color : ""}`}
                onClick={() => handleIsoClassChange(iso.code === selectedIsoClass ? null : iso.code)}
              >
                {iso.code} {iso.label_zh}
              </Button>
            ))}
          </div>

          {/* 清空筛选 */}
          {hasAnyFilter && (
            <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={handleReset}>
              清空筛选
            </Button>
          )}
        </div>

        {/* 变型标签（仅选中子分类时显示） */}
        {currentSub && currentSub.variants.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-medium text-muted-foreground">变型</span>
            <Button
              variant={!selectedVariant ? "secondary" : "ghost"}
              size="sm"
              className="h-7 text-xs"
              onClick={() => handleVariantChange(null)}
            >
              全部
            </Button>
            {currentSub.variants.map((v) => (
              <Button
                key={v.id}
                variant={selectedVariant === v.id ? "default" : "outline"}
                size="sm"
                className="h-7 text-xs"
                onClick={() => handleVariantChange(v.id === selectedVariant ? null : v.id)}
              >
                {v.label_zh}
              </Button>
            ))}
          </div>
        )}
      </div>

      {/* ④ 结果统计 */}
      <div className="mb-3 text-sm text-muted-foreground">
        {loading ? (
          "加载中..."
        ) : total > 0 ? (
          <>
            共 {total} 条刀具
            {total > pageSize && (
              <>，当前第 {page * pageSize + 1}–{Math.min((page + 1) * pageSize, total)} 条</>
            )}
          </>
        ) : hasAnyFilter ? (
          "当前筛选条件下无匹配刀具，请调整筛选条件"
        ) : (
          "暂无刀具数据"
        )}
      </div>

      {/* ⑤ 刀具卡片网格 */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {cutters.map((cutter) => (
          <Card
            key={cutter.id}
            className="cursor-pointer transition-shadow hover:shadow-md"
            onClick={() => navigate(`/cutter/${cutter.id}`)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-start gap-3">
                <img
                  src={cutter.image_url || "/images/cutters/placeholder.svg"}
                  alt={cutter.name}
                  className="h-16 w-16 shrink-0 rounded-md border object-cover"
                />
                <div className="min-w-0">
                  <CardTitle className="text-sm font-medium leading-tight">
                    {cutter.name}
                  </CardTitle>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {cutter.model_number}
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="mb-3 flex flex-wrap gap-1">
                <Badge variant="secondary">
                  {categoryLabels[cutter.cutter_type.category] ?? cutter.cutter_type.category}
                </Badge>
                {cutter.cutter_type.variant && (
                  <Badge variant="outline">{cutter.cutter_type.variant}</Badge>
                )}
                {cutter.material.coating_type && (
                  <Badge variant="outline">{cutter.material.coating_type}</Badge>
                )}
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/cutter/${cutter.id}`);
                  }}
                >
                  详情
                </Button>
                <Button
                  size="sm"
                  variant={isInCompare(cutter.id) ? "destructive" : "outline"}
                  onClick={(e) => {
                    e.stopPropagation();
                    isInCompare(cutter.id) ? removeItem(cutter.id) : addItem(cutter);
                  }}
                >
                  {isInCompare(cutter.id) ? "移除对比" : "加入对比"}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ⑥ 分页 */}
      {total > pageSize && (
        <Pagination
          total={total}
          pageSize={pageSize}
          currentPage={page}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
}
