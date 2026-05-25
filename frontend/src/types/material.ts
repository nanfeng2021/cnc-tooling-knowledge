export interface ISOClass {
  code: string;
  label_zh: string;
  label_en: string;
  color: string;
}

export const ISO_CLASSES: ISOClass[] = [
  { code: "P", label_zh: "钢", label_en: "Steel", color: "bg-blue-100 text-blue-800" },
  { code: "M", label_zh: "不锈钢", label_en: "Stainless", color: "bg-yellow-100 text-yellow-800" },
  { code: "K", label_zh: "铸铁", label_en: "Cast Iron", color: "bg-red-100 text-red-800" },
  { code: "N", label_zh: "非铁金属", label_en: "Non-ferrous", color: "bg-green-100 text-green-800" },
  { code: "S", label_zh: "高温合金", label_en: "Superalloy", color: "bg-orange-100 text-orange-800" },
  { code: "H", label_zh: "硬材", label_en: "Hard Material", color: "bg-gray-100 text-gray-800" },
];
