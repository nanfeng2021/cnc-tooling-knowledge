import type { Cutter, PaginatedResponse, SearchResult } from "@/types/cutter";
import type { CategoryTree } from "@/types/category";
import type { Manufacturer } from "@/types/manufacturer";
import type { ParameterRecommendation } from "@/types/recommendation";
import type { MachiningScenario, ScenarioMatchResponse } from "@/types/scenario";
import type { QAResponse } from "@/types/qa";
import type { SimilarToolResponse } from "@/types/similar";
import type { GCodeSuggestion } from "@/types/gcode";
import {
  allCutters,
  allCategories,
  allManufacturers,
  findCutterById,
  findManufacturerById,
  filterCuttersByCategory,
  filterCuttersBySubcategory,
  filterCuttersByManufacturer,
  filterCuttersByVariant,
  filterCuttersByIsoClass,
  searchCutters as mockSearch,
} from "./mocks";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";
const USE_MOCK = import.meta.env.VITE_API_MODE === "mock";

// ============ Helper ============

/**
 * 统一的API请求函数，包含错误处理和JSON解析
 */
async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const errorBody = await res.text().catch(() => "Unknown error");
      throw new Error(`API error ${res.status}: ${errorBody}`);
    }
    return await res.json();
  } catch (error) {
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      throw new Error("Network error: Unable to connect to the server");
    }
    throw error;
  }
}

function paginate<T>(items: T[], limit: number, offset: number): PaginatedResponse<T> {
  return {
    items: items.slice(offset, offset + limit),
    total: items.length,
    limit,
    offset,
  };
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ============ Cutter Service ============

export const cutterService = {
  async list(params?: {
    category?: string;
    subcategory?: string;
    variant?: string;
    iso_class?: string;
    manufacturer_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<PaginatedResponse<Cutter>> {
    const limit = params?.limit ?? 20;
    const offset = params?.offset ?? 0;

    if (USE_MOCK) {
      await delay(150);
      let results = [...allCutters];
      if (params?.category) results = filterCuttersByCategory(params.category);
      if (params?.subcategory) results = filterCuttersBySubcategory(params.subcategory);
      if (params?.variant) results = filterCuttersByVariant(params.variant);
      if (params?.manufacturer_id) results = filterCuttersByManufacturer(params.manufacturer_id);
      if (params?.iso_class) results = filterCuttersByIsoClass(params.iso_class);
      return paginate(results, limit, offset);
    }

    const sp = new URLSearchParams();
    if (params?.category) sp.set("category", params.category);
    if (params?.subcategory) sp.set("subcategory", params.subcategory);
    if (params?.variant) sp.set("variant", params.variant);
    if (params?.iso_class) sp.set("iso_class", params.iso_class);
    if (params?.manufacturer_id) sp.set("manufacturer_id", params.manufacturer_id);
    sp.set("limit", String(limit));
    sp.set("offset", String(offset));

    return apiFetch<PaginatedResponse<Cutter>>(`${API_BASE_URL}/cutters?${sp}`);
  },

  async getById(id: string): Promise<Cutter | null> {
    if (USE_MOCK) {
      await delay(100);
      return findCutterById(id) ?? null;
    }
    try {
      return await apiFetch<Cutter>(`${API_BASE_URL}/cutters/${id}`);
    } catch (error) {
      return null;
    }
  },
};

// ============ Search Service ============

export const searchService = {
  async search(query: string, limit?: number, offset?: number): Promise<PaginatedResponse<SearchResult>> {
    const l = limit ?? 20;
    const o = offset ?? 0;

    if (USE_MOCK) {
      await delay(200);
      const results = mockSearch(query).map((r) => ({
        cutter: r.cutter,
        relevance_score: r.score,
      }));
      return paginate(results, l, o);
    }

    const sp = new URLSearchParams();
    sp.set("q", query);
    sp.set("limit", String(l));
    sp.set("offset", String(o));

    return apiFetch<PaginatedResponse<SearchResult>>(`${API_BASE_URL}/search?${sp}`);
  },
};

// ============ Category Service ============

/** 为 CategoryTree 添加 id/label_zh 别名，供 UI 组件统一使用 */
function normalizeCategories(cats: CategoryTree[]): CategoryTree[] {
  return cats.map((c) => ({
    ...c,
    id: c.category,
    label_zh: c.category_zh,
    subcategories: c.subcategories.map((s) => ({
      ...s,
      id: s.subcategory,
      label_zh: s.subcategory_zh,
      variants: s.variants.map((v) => ({
        ...v,
        id: v.variant,
        label_zh: v.variant_zh,
      })),
    })),
  }));
}

export const categoryService = {
  async list(): Promise<CategoryTree[]> {
    if (USE_MOCK) {
      await delay(100);
      return normalizeCategories(allCategories as unknown as CategoryTree[]);
    }
    const data = await apiFetch<CategoryTree[]>(`${API_BASE_URL}/categories`);
    return normalizeCategories(data);
  },
};

// ============ Manufacturer Service ============

export const manufacturerService = {
  async list(): Promise<Manufacturer[]> {
    if (USE_MOCK) {
      await delay(100);
      return allManufacturers;
    }
    const data = await apiFetch<any>(`${API_BASE_URL}/manufacturers`);
    // API返回分页格式 { items: [], total: 0 }，提取items数组
    return Array.isArray(data) ? data : data.items ?? [];
  },

  async getById(id: string): Promise<Manufacturer | null> {
    if (USE_MOCK) {
      await delay(80);
      return findManufacturerById(id) ?? null;
    }
    try {
      return await apiFetch<Manufacturer>(`${API_BASE_URL}/manufacturers/${id}`);
    } catch (error) {
      return null;
    }
  },
};

// ============ Recommendation Service ============

const MATERIAL_MAP: Record<string, string> = {
  P: "steel",
  M: "stainless",
  K: "cast_iron",
  N: "aluminum",
  S: "superalloy",
  H: "hardened",
};

function mockRecommend(
  material: string,
  operation: string,
  _diameter?: number,
): ParameterRecommendation {
  const iso = MATERIAL_MAP[material] ? material : material.toUpperCase();
  const suffix = MATERIAL_MAP[iso] ?? material;
  const matching = allCutters.filter(
    (c) =>
      c.cutter_type.category === operation &&
      c.compatible_materials.some((m) => m.toUpperCase() === iso),
  );
  const params: Record<string, { min_value: number; max_value: number; avg_value: number; unit: string }> = {};
  const keys = [`vc_${suffix}`, operation === "milling" ? `fz_${suffix}` : `fn_${suffix}`, "ap_max", "ae_max"];
  for (const key of keys) {
    const vals = matching.map((c) => c.recommended_parameters[key]).filter((v) => v != null);
    if (vals.length > 0) {
      const unit = key.startsWith("vc") ? "m/min" : key.startsWith("fz") ? "mm/tooth" : key.startsWith("fn") ? "mm/rev" : "mm";
      params[key] = {
        min_value: Math.min(...vals),
        max_value: Math.max(...vals),
        avg_value: vals.reduce((a, b) => a + b, 0) / vals.length,
        unit,
      };
    }
  }
  return {
    workpiece_material: material,
    iso_code: iso,
    operation_type: operation,
    target_diameter: _diameter ?? null,
    parameters: params,
    source_cutters: matching.slice(0, 5),
    candidate_count: matching.length,
  };
}

export const recommendationService = {
  async getParameters(
    workpieceMaterial: string,
    operationType: string,
    targetDiameter?: number,
  ): Promise<ParameterRecommendation> {
    if (USE_MOCK) {
      await delay(200);
      return mockRecommend(workpieceMaterial, operationType, targetDiameter);
    }
    const sp = new URLSearchParams();
    sp.set("workpiece_material", workpieceMaterial);
    sp.set("operation_type", operationType);
    if (targetDiameter) sp.set("target_diameter", String(targetDiameter));
    return apiFetch<ParameterRecommendation>(`${API_BASE_URL}/recommendations/parameters?${sp}`);
  },
};

// ============ Scenario Service ============

export const scenarioService = {
  async match(scenario: MachiningScenario): Promise<ScenarioMatchResponse> {
    if (USE_MOCK) {
      await delay(250);
      // Simplified mock scoring
      const results = allCutters
        .map((c) => {
          let score = 0;
          if (c.cutter_type.category === scenario.category) score += 0.3;
          if (c.compatible_materials.some((m) => m.toUpperCase() === scenario.material_iso_code.toUpperCase())) score += 0.25;
          if (scenario.subcategory && c.cutter_type.subcategory === scenario.subcategory) score += 0.15;
          if (scenario.variant && c.cutter_type.variant === scenario.variant) score += 0.1;
          if (!scenario.subcategory) score += 0.075;
          if (!scenario.variant) score += 0.05;
          score += 0.1; // diameter neutral
          score += 0.05; // partial params
          return { cutter: c, score: Math.min(score, 1), score_breakdown: { category: c.cutter_type.category === scenario.category ? 1 : 0, material: c.compatible_materials.some((m) => m.toUpperCase() === scenario.material_iso_code.toUpperCase()) ? 1 : 0 } };
        })
        .filter((r) => r.score >= (scenario.min_score ?? 0))
        .sort((a, b) => b.score - a.score)
        .slice(0, scenario.top_k ?? 10);
      return { items: results, total: results.length };
    }
    return apiFetch<ScenarioMatchResponse>(`${API_BASE_URL}/scenarios/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scenario),
    });
  },
};

// ============ Q&A Service ============

export const qaService = {
  async ask(question: string, topK?: number): Promise<QAResponse> {
    if (USE_MOCK) {
      await delay(300);
      const keywords = question.toLowerCase();
      const matching = allCutters.filter(
        (c) =>
          keywords.includes(c.cutter_type.category) ||
          c.name.toLowerCase().includes(keywords) ||
          c.compatible_materials.some((m) => keywords.includes(m.toLowerCase())),
      );
      const sources = matching.slice(0, topK ?? 5).map((c, i) => ({
        cutter_id: c.id,
        cutter_name: c.name,
        relevance_score: 0.9 - i * 0.1,
        category: c.cutter_type.category,
        diameter: c.geometry.diameter,
        summary: `${c.cutter_type.category} | ${c.geometry.diameter}mm | ${c.material.substrate}`,
      }));
      return {
        question,
        answer: sources.length > 0
          ? `Found ${sources.length} relevant cutter(s) for your question.`
          : "No relevant cutters found. Try rephrasing your question.",
        sources,
        confidence: sources.length > 0 ? 0.8 : 0.0,
      };
    }
    return apiFetch<QAResponse>(`${API_BASE_URL}/qa/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: topK ?? 5 }),
    });
  },
};

// ============ Similar Tool Service ============

export const similarService = {
  async findSimilar(cutterId: string, topK?: number): Promise<SimilarToolResponse> {
    if (USE_MOCK) {
      await delay(200);
      const source = findCutterById(cutterId);
      if (!source) {
        return { source_cutter_id: cutterId, source_cutter_name: "Unknown", similar_cutters: [], count: 0 };
      }
      const similar = allCutters
        .filter((c) => c.id !== cutterId && c.cutter_type.category === source.cutter_type.category)
        .slice(0, topK ?? 5)
        .map((c, i) => ({
          cutter_id: c.id,
          cutter_name: c.name,
          similarity_score: 0.9 - i * 0.1,
          category: c.cutter_type.category,
          diameter: c.geometry.diameter,
          substrate: c.material.substrate,
        }));
      return {
        source_cutter_id: cutterId,
        source_cutter_name: source.name,
        similar_cutters: similar,
        count: similar.length,
      };
    }
    return apiFetch<SimilarToolResponse>(`${API_BASE_URL}/similar/find`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cutter_id: cutterId, top_k: topK ?? 5 }),
    });
  },
};

// ============ G-code Service ============

export const gcodeService = {
  async generate(params: {
    cutterId: string;
    operation: string;
    workpieceMaterial: string;
    diameter?: number;
    width?: number;
    length?: number;
    depth?: number;
  }): Promise<GCodeSuggestion> {
    if (USE_MOCK) {
      await delay(250);
      return {
        operation: params.operation,
        gcode_lines: [
          "%",
          `O1000 (${params.operation.toUpperCase()})`,
          "G90 G21",
          "S3000 M3",
          "G0 X0 Y0",
          "G1 Z-2.0 F500",
          "G1 X50.0 F800",
          "G0 Z50.0",
          "M5",
          "M30",
          "%",
        ],
        gcode_text: "Mock G-code",
        description: `${params.operation} operation (mock)`,
        spindle_rpm: 3000,
        feed_rate: 800,
        parameters_used: { vc: 180, fz: 0.05, spindle_rpm: 3000, feed_rate: 800 },
        warnings: [],
      };
    }
    return apiFetch<GCodeSuggestion>(`${API_BASE_URL}/gcode/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cutter_id: params.cutterId,
        operation: params.operation,
        workpiece_material: params.workpieceMaterial,
        diameter: params.diameter,
        width: params.width,
        length: params.length,
        depth: params.depth,
      }),
    });
  },
};
