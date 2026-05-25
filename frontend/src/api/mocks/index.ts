import type { Cutter } from "@/types/cutter";
import type { CategoryTree } from "@/types/category";
import type { Manufacturer } from "@/types/manufacturer";
import { categoryTree as categories } from "./categories";
import { manufacturers } from "./manufacturers";
import { millingCutters } from "./cutters/milling";
import { turningCutters } from "./cutters/turning";
import { holeMakingCutters } from "./cutters/hole_making";
import { threadingCutters } from "./cutters/threading";
import { gearCuttingCutters } from "./cutters/gear_cutting";

export const allCutters: Cutter[] = [
  ...millingCutters,
  ...turningCutters,
  ...holeMakingCutters,
  ...threadingCutters,
  ...gearCuttingCutters,
];

export const allCategories: CategoryTree[] = categories;
export const allManufacturers: Manufacturer[] = manufacturers;

// 按 ID 查找
export function findCutterById(id: string): Cutter | undefined {
  return allCutters.find((c) => c.id === id);
}

export function findManufacturerById(id: string): Manufacturer | undefined {
  return allManufacturers.find((m) => m.id === id);
}

// 按分类过滤
export function filterCuttersByCategory(category: string): Cutter[] {
  return allCutters.filter((c) => c.cutter_type.category === category);
}

export function filterCuttersBySubcategory(subcategory: string): Cutter[] {
  return allCutters.filter((c) => c.cutter_type.subcategory === subcategory);
}

export function filterCuttersByManufacturer(manufacturerId: string): Cutter[] {
  return allCutters.filter((c) => c.manufacturer_id === manufacturerId);
}

export function filterCuttersByVariant(variant: string): Cutter[] {
  return allCutters.filter((c) => c.cutter_type.variant === variant);
}

export function filterCuttersByIsoClass(isoClass: string): Cutter[] {
  return allCutters.filter((c) => c.compatible_materials.includes(isoClass));
}

// 简单关键词搜索
export function searchCutters(query: string): { cutter: Cutter; score: number }[] {
  const q = query.toLowerCase();
  return allCutters
    .map((cutter) => {
      let score = 0;
      const name = cutter.name.toLowerCase();
      const model = (cutter.model_number ?? "").toLowerCase();

      if (name.includes(q)) score += 10;
      if (model.includes(q)) score += 8;
      if (cutter.cutter_type.category.includes(q)) score += 5;
      if (cutter.cutter_type.subcategory.includes(q)) score += 5;
      if (cutter.cutter_type.variant?.includes(q)) score += 4;
      if (cutter.compatible_materials.some((m) => m.toLowerCase() === q)) score += 3;
      if (cutter.material.coating_type?.toLowerCase().includes(q)) score += 2;
      if (cutter.material.substrate.toLowerCase().includes(q)) score += 2;
      cutter.usage_guidelines.forEach((g) => {
        if (g.toLowerCase().includes(q)) score += 1;
      });

      return { cutter, score };
    })
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score);
}
