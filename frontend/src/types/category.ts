export interface Variant {
  variant: string;
  variant_zh: string;
  variant_en: string;
  description?: string;
  /** 别名：同 variant */
  id: string;
  /** 别名：同 variant_zh */
  label_zh: string;
}

export interface Subcategory {
  subcategory: string;
  subcategory_zh: string;
  subcategory_en: string;
  variants: Variant[];
  /** 别名：同 subcategory */
  id: string;
  /** 别名：同 subcategory_zh */
  label_zh: string;
}

export interface CategoryTree {
  category: string;
  category_zh: string;
  category_en: string;
  icon: string;
  subcategories: Subcategory[];
  /** 别名：同 category */
  id: string;
  /** 别名：同 category_zh */
  label_zh: string;
}
