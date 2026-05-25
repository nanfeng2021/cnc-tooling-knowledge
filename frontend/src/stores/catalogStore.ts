import { create } from "zustand";
import type { Cutter } from "@/types/cutter";
import type { CategoryTree } from "@/types/category";
import type { Manufacturer } from "@/types/manufacturer";
import { cutterService, categoryService, manufacturerService } from "@/api/client";

interface CatalogState {
  categories: CategoryTree[];
  manufacturers: Manufacturer[];
  cutters: Cutter[];
  total: number;
  selectedCategory: string | null;
  selectedSubcategory: string | null;
  selectedVariant: string | null;
  selectedManufacturer: string | null;
  selectedIsoClass: string | null;
  page: number;
  pageSize: number;
  loading: boolean;
  setCategory: (cat: string | null) => void;
  setSubcategory: (sub: string | null) => void;
  setVariant: (variant: string | null) => void;
  setManufacturer: (mfr: string | null) => void;
  setIsoClass: (isoClass: string | null) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  resetFilters: () => void;
  fetchCategories: () => Promise<void>;
  fetchCutters: () => Promise<void>;
}

export const useCatalogStore = create<CatalogState>((set, get) => ({
  categories: [],
  manufacturers: [],
  cutters: [],
  total: 0,
  selectedCategory: null,
  selectedSubcategory: null,
  selectedVariant: null,
  selectedManufacturer: null,
  selectedIsoClass: null,
  page: 0,
  pageSize: 10,
  loading: false,

  setCategory: (cat) => set({
    selectedCategory: cat,
    selectedSubcategory: null,
    selectedVariant: null,
    page: 0,
  }),
  setSubcategory: (sub) => set({
    selectedSubcategory: sub,
    selectedVariant: null,
    page: 0,
  }),
  setVariant: (variant) => set({ selectedVariant: variant, page: 0 }),
  setManufacturer: (mfr) => set({ selectedManufacturer: mfr, page: 0 }),
  setIsoClass: (isoClass) => set({ selectedIsoClass: isoClass, page: 0 }),
  setPage: (page) => set({ page }),
  setPageSize: (size) => set({ pageSize: size, page: 0 }),
  resetFilters: () => set({
    selectedCategory: null,
    selectedSubcategory: null,
    selectedVariant: null,
    selectedManufacturer: null,
    selectedIsoClass: null,
    page: 0,
  }),

  fetchCategories: async () => {
    try {
      const [cats, mfrs] = await Promise.all([
        categoryService.list(),
        manufacturerService.list(),
      ]);
      set({ categories: cats, manufacturers: mfrs });
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      // 设置空数组防止页面崩溃
      set({ categories: [], manufacturers: [] });
    }
  },

  fetchCutters: async () => {
    const {
      selectedCategory, selectedSubcategory, selectedVariant,
      selectedManufacturer, selectedIsoClass, page, pageSize,
    } = get();
    set({ loading: true });
    try {
      const res = await cutterService.list({
        category: selectedSubcategory ? undefined : selectedCategory ?? undefined,
        subcategory: selectedSubcategory ?? undefined,
        variant: selectedVariant ?? undefined,
        manufacturer_id: selectedManufacturer ?? undefined,
        iso_class: selectedIsoClass ?? undefined,
        limit: pageSize,
        offset: page * pageSize,
      });
      set({ cutters: res.items, total: res.total, loading: false });
    } catch {
      set({ loading: false });
    }
  },
}));
