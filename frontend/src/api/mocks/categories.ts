import type { CategoryTree } from "@/types/category";

export const categoryTree: CategoryTree[] = [
  {
    category: "turning", category_zh: "车削刀具", category_en: "Turning", id: "turning", label_zh: "车削刀具",
    icon: "RotateCcw",
    subcategories: [
      {
        subcategory: "turning_external", subcategory_zh: "外圆车刀", subcategory_en: "External Turning", id: "turning_external", label_zh: "外圆车刀",
        variants: [
          { variant: "roughing", variant_zh: "粗车外圆刀", variant_en: "Roughing", id: "roughing", label_zh: "粗车外圆刀" },
          { variant: "finishing", variant_zh: "精车外圆刀", variant_en: "Finishing", id: "finishing", label_zh: "精车外圆刀" },
          { variant: "light", variant_zh: "轻切削外圆刀", variant_en: "Light Cutting", id: "light", label_zh: "轻切削外圆刀" },
          { variant: "heavy", variant_zh: "重切削外圆刀", variant_en: "Heavy Cutting", id: "heavy", label_zh: "重切削外圆刀" },
          { variant: "miniature", variant_zh: "小型外圆刀", variant_en: "Miniature", id: "miniature", label_zh: "小型外圆刀" },
        ],
      },
      {
        subcategory: "turning_internal", subcategory_zh: "内孔车刀", subcategory_en: "Internal Turning", id: "turning_internal", label_zh: "内孔车刀",
        variants: [
          { variant: "through_hole", variant_zh: "通孔车刀", variant_en: "Through Hole", id: "through_hole", label_zh: "通孔车刀" },
          { variant: "blind_hole", variant_zh: "盲孔车刀", variant_en: "Blind Hole", id: "blind_hole", label_zh: "盲孔车刀" },
          { variant: "micro", variant_zh: "微小径内孔车刀", variant_en: "Micro Bore", id: "micro", label_zh: "微小径内孔车刀" },
        ],
      },
      {
        subcategory: "turning_facing", subcategory_zh: "端面车刀", subcategory_en: "Facing", id: "turning_facing", label_zh: "端面车刀",
        variants: [
          { variant: "external", variant_zh: "外端面车刀", variant_en: "External Facing", id: "external", label_zh: "外端面车刀" },
          { variant: "internal", variant_zh: "内端面车刀", variant_en: "Internal Facing", id: "internal", label_zh: "内端面车刀" },
        ],
      },
      {
        subcategory: "turning_grooving", subcategory_zh: "切断刀/切槽刀", subcategory_en: "Grooving", id: "turning_grooving", label_zh: "切断刀/切槽刀",
        variants: [
          { variant: "parting", variant_zh: "切断刀", variant_en: "Parting Off", id: "parting", label_zh: "切断刀" },
          { variant: "external", variant_zh: "外圆切槽刀", variant_en: "External Groove", id: "external", label_zh: "外圆切槽刀" },
          { variant: "internal", variant_zh: "内孔切槽刀", variant_en: "Internal Groove", id: "internal", label_zh: "内孔切槽刀" },
          { variant: "face", variant_zh: "端面切槽刀", variant_en: "Face Groove", id: "face", label_zh: "端面切槽刀" },
          { variant: "narrow", variant_zh: "窄槽刀", variant_en: "Narrow Groove", id: "narrow", label_zh: "窄槽刀" },
          { variant: "wide", variant_zh: "宽槽刀", variant_en: "Wide Groove", id: "wide", label_zh: "宽槽刀" },
        ],
      },
      {
        subcategory: "turning_threading", subcategory_zh: "螺纹车刀", subcategory_en: "Threading", id: "turning_threading", label_zh: "螺纹车刀",
        variants: [
          { variant: "external", variant_zh: "外螺纹车刀", variant_en: "External Thread", id: "external", label_zh: "外螺纹车刀" },
          { variant: "internal", variant_zh: "内螺纹车刀", variant_en: "Internal Thread", id: "internal", label_zh: "内螺纹车刀" },
          { variant: "pipe", variant_zh: "管螺纹车刀", variant_en: "Pipe Thread", id: "pipe", label_zh: "管螺纹车刀" },
        ],
      },
      {
        subcategory: "turning_profiling", subcategory_zh: "仿形车刀", subcategory_en: "Profiling", id: "turning_profiling", label_zh: "仿形车刀",
        variants: [
          { variant: "rough", variant_zh: "粗仿形车刀", variant_en: "Rough Profiling", id: "rough", label_zh: "粗仿形车刀" },
          { variant: "finish", variant_zh: "精仿形车刀", variant_en: "Finish Profiling", id: "finish", label_zh: "精仿形车刀" },
        ],
      },
    ],
  },
  {
    category: "milling", category_zh: "铣削刀具", category_en: "Milling", id: "milling", label_zh: "铣削刀具",
    icon: "CircleDot",
    subcategories: [
      {
        subcategory: "milling_end_mill", subcategory_zh: "立铣刀", subcategory_en: "End Mill", id: "milling_end_mill", label_zh: "立铣刀",
        variants: [
          { variant: "square", variant_zh: "方肩立铣刀", variant_en: "Square", id: "square", label_zh: "方肩立铣刀" },
          { variant: "ball_nose", variant_zh: "球头立铣刀", variant_en: "Ball Nose", id: "ball_nose", label_zh: "球头立铣刀" },
          { variant: "bull_nose", variant_zh: "圆鼻立铣刀", variant_en: "Bull Nose", id: "bull_nose", label_zh: "圆鼻立铣刀" },
          { variant: "high_feed", variant_zh: "高进给立铣刀", variant_en: "High Feed", id: "high_feed", label_zh: "高进给立铣刀" },
          { variant: "roughing", variant_zh: "粗铣立铣刀", variant_en: "Roughing", id: "roughing", label_zh: "粗铣立铣刀" },
          { variant: "chamfer", variant_zh: "倒角立铣刀", variant_en: "Chamfer", id: "chamfer", label_zh: "倒角立铣刀" },
          { variant: "micro", variant_zh: "微径立铣刀", variant_en: "Micro", id: "micro", label_zh: "微径立铣刀" },
          { variant: "taper", variant_zh: "锥度立铣刀", variant_en: "Taper", id: "taper", label_zh: "锥度立铣刀" },
        ],
      },
      {
        subcategory: "milling_face_mill", subcategory_zh: "面铣刀", subcategory_en: "Face Mill", id: "milling_face_mill", label_zh: "面铣刀",
        variants: [
          { variant: "indexable", variant_zh: "可转位面铣刀", variant_en: "Indexable", id: "indexable", label_zh: "可转位面铣刀" },
          { variant: "brazed", variant_zh: "焊接式面铣刀", variant_en: "Brazed", id: "brazed", label_zh: "焊接式面铣刀" },
          { variant: "fine_pitch", variant_zh: "密齿面铣刀", variant_en: "Fine Pitch", id: "fine_pitch", label_zh: "密齿面铣刀" },
          { variant: "coarse_pitch", variant_zh: "粗齿面铣刀", variant_en: "Coarse Pitch", id: "coarse_pitch", label_zh: "粗齿面铣刀" },
        ],
      },
      {
        subcategory: "milling_corncob", subcategory_zh: "玉米铣刀", subcategory_en: "Corncob", id: "milling_corncob", label_zh: "玉米铣刀",
        variants: [
          { variant: "standard", variant_zh: "等径玉米铣刀", variant_en: "Standard", id: "standard", label_zh: "等径玉米铣刀" },
          { variant: "tapered", variant_zh: "锥度玉米铣刀", variant_en: "Tapered", id: "tapered", label_zh: "锥度玉米铣刀" },
        ],
      },
      {
        subcategory: "milling_t_slot", subcategory_zh: "T型槽铣刀", subcategory_en: "T-Slot", id: "milling_t_slot", label_zh: "T型槽铣刀",
        variants: [
          { variant: "standard", variant_zh: "标准T型槽铣刀", variant_en: "Standard", id: "standard", label_zh: "标准T型槽铣刀" },
        ],
      },
      {
        subcategory: "milling_keyway", subcategory_zh: "键槽铣刀", subcategory_en: "Keyway", id: "milling_keyway", label_zh: "键槽铣刀",
        variants: [
          { variant: "standard", variant_zh: "标准键槽铣刀", variant_en: "Standard", id: "standard", label_zh: "标准键槽铣刀" },
          { variant: "woodruff", variant_zh: "半圆键槽铣刀", variant_en: "Woodruff", id: "woodruff", label_zh: "半圆键槽铣刀" },
        ],
      },
      {
        subcategory: "milling_angle", subcategory_zh: "角度铣刀", subcategory_en: "Angle", id: "milling_angle", label_zh: "角度铣刀",
        variants: [
          { variant: "single", variant_zh: "单角铣刀", variant_en: "Single Angle", id: "single", label_zh: "单角铣刀" },
          { variant: "double", variant_zh: "双角铣刀", variant_en: "Double Angle", id: "double", label_zh: "双角铣刀" },
        ],
      },
      {
        subcategory: "milling_form", subcategory_zh: "成形铣刀", subcategory_en: "Form", id: "milling_form", label_zh: "成形铣刀",
        variants: [
          { variant: "gear", variant_zh: "齿轮铣刀", variant_en: "Gear", id: "gear", label_zh: "齿轮铣刀" },
          { variant: "convex", variant_zh: "凸半圆铣刀", variant_en: "Convex", id: "convex", label_zh: "凸半圆铣刀" },
          { variant: "concave", variant_zh: "凹半圆铣刀", variant_en: "Concave", id: "concave", label_zh: "凹半圆铣刀" },
        ],
      },
      {
        subcategory: "milling_saw", subcategory_zh: "锯片铣刀", subcategory_en: "Saw", id: "milling_saw", label_zh: "锯片铣刀",
        variants: [
          { variant: "solid", variant_zh: "整体锯片", variant_en: "Solid", id: "solid", label_zh: "整体锯片" },
          { variant: "inserted", variant_zh: "镶齿锯片", variant_en: "Inserted", id: "inserted", label_zh: "镶齿锯片" },
        ],
      },
    ],
  },
  {
    category: "hole_making", category_zh: "孔加工刀具", category_en: "Hole Making", id: "hole_making", label_zh: "孔加工刀具",
    icon: "Drill",
    subcategories: [
      {
        subcategory: "hole_drill", subcategory_zh: "钻头", subcategory_en: "Drill", id: "hole_drill", label_zh: "钻头",
        variants: [
          { variant: "twist", variant_zh: "麻花钻", variant_en: "Twist", id: "twist", label_zh: "麻花钻" },
          { variant: "center", variant_zh: "中心钻", variant_en: "Center", id: "center", label_zh: "中心钻" },
          { variant: "spot", variant_zh: "定心钻", variant_en: "Spot", id: "spot", label_zh: "定心钻" },
          { variant: "core", variant_zh: "扩孔钻", variant_en: "Core", id: "core", label_zh: "扩孔钻" },
          { variant: "step", variant_zh: "阶梯钻", variant_en: "Step", id: "step", label_zh: "阶梯钻" },
          { variant: "indexable", variant_zh: "可转位钻头", variant_en: "Indexable", id: "indexable", label_zh: "可转位钻头" },
          { variant: "gun", variant_zh: "深孔钻", variant_en: "Gun", id: "gun", label_zh: "深孔钻" },
          { variant: "solid_carbide", variant_zh: "硬质合金定柄钻", variant_en: "Solid Carbide", id: "solid_carbide", label_zh: "硬质合金定柄钻" },
        ],
      },
      {
        subcategory: "hole_reamer", subcategory_zh: "铰刀", subcategory_en: "Reamer", id: "hole_reamer", label_zh: "铰刀",
        variants: [
          { variant: "straight", variant_zh: "直槽铰刀", variant_en: "Straight", id: "straight", label_zh: "直槽铰刀" },
          { variant: "spiral", variant_zh: "螺旋槽铰刀", variant_en: "Spiral", id: "spiral", label_zh: "螺旋槽铰刀" },
          { variant: "taper", variant_zh: "锥度铰刀", variant_en: "Taper", id: "taper", label_zh: "锥度铰刀" },
          { variant: "adjustable", variant_zh: "可调铰刀", variant_en: "Adjustable", id: "adjustable", label_zh: "可调铰刀" },
          { variant: "machine", variant_zh: "机用铰刀", variant_en: "Machine", id: "machine", label_zh: "机用铰刀" },
          { variant: "hand", variant_zh: "手用铰刀", variant_en: "Hand", id: "hand", label_zh: "手用铰刀" },
        ],
      },
      {
        subcategory: "hole_boring", subcategory_zh: "镗刀", subcategory_en: "Boring", id: "hole_boring", label_zh: "镗刀",
        variants: [
          { variant: "rough", variant_zh: "粗镗刀", variant_en: "Rough", id: "rough", label_zh: "粗镗刀" },
          { variant: "fine", variant_zh: "精镗刀", variant_en: "Fine", id: "fine", label_zh: "精镗刀" },
          { variant: "micro", variant_zh: "微调镗刀", variant_en: "Micro", id: "micro", label_zh: "微调镗刀" },
          { variant: "double", variant_zh: "双刃镗刀", variant_en: "Double Edge", id: "double", label_zh: "双刃镗刀" },
        ],
      },
      {
        subcategory: "hole_countersink", subcategory_zh: "锪钻", subcategory_en: "Countersink", id: "hole_countersink", label_zh: "锪钻",
        variants: [
          { variant: "chamfer", variant_zh: "沉头锪钻", variant_en: "Chamfer", id: "chamfer", label_zh: "沉头锪钻" },
          { variant: "plane", variant_zh: "锪平面钻", variant_en: "Counterbore", id: "plane", label_zh: "锪平面钻" },
        ],
      },
    ],
  },
  {
    category: "threading", category_zh: "螺纹加工刀具", category_en: "Threading", id: "threading", label_zh: "螺纹加工刀具",
    icon: "Wrench",
    subcategories: [
      {
        subcategory: "threading_tap", subcategory_zh: "丝锥", subcategory_en: "Tap", id: "threading_tap", label_zh: "丝锥",
        variants: [
          { variant: "machine", variant_zh: "机用丝锥", variant_en: "Machine", id: "machine", label_zh: "机用丝锥" },
          { variant: "hand", variant_zh: "手用丝锥", variant_en: "Hand", id: "hand", label_zh: "手用丝锥" },
          { variant: "spiral_flute", variant_zh: "螺旋槽丝锥", variant_en: "Spiral Flute", id: "spiral_flute", label_zh: "螺旋槽丝锥" },
          { variant: "straight_flute", variant_zh: "直槽丝锥", variant_en: "Straight Flute", id: "straight_flute", label_zh: "直槽丝锥" },
          { variant: "spiral_point", variant_zh: "螺尖丝锥", variant_en: "Spiral Point", id: "spiral_point", label_zh: "螺尖丝锥" },
          { variant: "forming", variant_zh: "挤压丝锥", variant_en: "Forming", id: "forming", label_zh: "挤压丝锥" },
          { variant: "pipe", variant_zh: "管螺纹丝锥", variant_en: "Pipe", id: "pipe", label_zh: "管螺纹丝锥" },
          { variant: "taper_pipe", variant_zh: "锥管螺纹丝锥", variant_en: "Taper Pipe", id: "taper_pipe", label_zh: "锥管螺纹丝锥" },
        ],
      },
      {
        subcategory: "threading_die", subcategory_zh: "板牙", subcategory_en: "Die", id: "threading_die", label_zh: "板牙",
        variants: [
          { variant: "round", variant_zh: "圆板牙", variant_en: "Round", id: "round", label_zh: "圆板牙" },
          { variant: "hex", variant_zh: "六角板牙", variant_en: "Hex", id: "hex", label_zh: "六角板牙" },
        ],
      },
      {
        subcategory: "threading_mill", subcategory_zh: "螺纹铣刀", subcategory_en: "Thread Mill", id: "threading_mill", label_zh: "螺纹铣刀",
        variants: [
          { variant: "single_point", variant_zh: "单刃螺纹铣刀", variant_en: "Single Point", id: "single_point", label_zh: "单刃螺纹铣刀" },
          { variant: "multi_point", variant_zh: "多刃螺纹铣刀", variant_en: "Multi Point", id: "multi_point", label_zh: "多刃螺纹铣刀" },
          { variant: "solid", variant_zh: "整体螺纹铣刀", variant_en: "Solid", id: "solid", label_zh: "整体螺纹铣刀" },
          { variant: "indexable", variant_zh: "可转位螺纹铣刀", variant_en: "Indexable", id: "indexable", label_zh: "可转位螺纹铣刀" },
        ],
      },
      {
        subcategory: "threading_turning", subcategory_zh: "螺纹车刀", subcategory_en: "Thread Turning", id: "threading_turning", label_zh: "螺纹车刀",
        variants: [
          { variant: "external", variant_zh: "外螺纹车刀", variant_en: "External", id: "external", label_zh: "外螺纹车刀" },
          { variant: "internal", variant_zh: "内螺纹车刀", variant_en: "Internal", id: "internal", label_zh: "内螺纹车刀" },
          { variant: "pipe", variant_zh: "管螺纹车刀", variant_en: "Pipe", id: "pipe", label_zh: "管螺纹车刀" },
        ],
      },
    ],
  },
  {
    category: "gear_cutting", category_zh: "齿轮加工刀具", category_en: "Gear Cutting", id: "gear_cutting", label_zh: "齿轮加工刀具",
    icon: "Cog",
    subcategories: [
      {
        subcategory: "gear_hob", subcategory_zh: "滚刀", subcategory_en: "Hob", id: "gear_hob", label_zh: "滚刀",
        variants: [
          { variant: "standard", variant_zh: "齿轮滚刀", variant_en: "Standard", id: "standard", label_zh: "齿轮滚刀" },
          { variant: "pre_shave", variant_zh: "剃前滚刀", variant_en: "Pre-Shave", id: "pre_shave", label_zh: "剃前滚刀" },
          { variant: "pre_grind", variant_zh: "磨前滚刀", variant_en: "Pre-Grind", id: "pre_grind", label_zh: "磨前滚刀" },
          { variant: "worm_wheel", variant_zh: "蜗轮滚刀", variant_en: "Worm Wheel", id: "worm_wheel", label_zh: "蜗轮滚刀" },
          { variant: "sprocket", variant_zh: "链轮滚刀", variant_en: "Sprocket", id: "sprocket", label_zh: "链轮滚刀" },
          { variant: "spline", variant_zh: "渐开线花键滚刀", variant_en: "Spline", id: "spline", label_zh: "渐开线花键滚刀" },
        ],
      },
      {
        subcategory: "gear_shaper", subcategory_zh: "插齿刀", subcategory_en: "Shaper", id: "gear_shaper", label_zh: "插齿刀",
        variants: [
          { variant: "disc", variant_zh: "盘形插齿刀", variant_en: "Disc", id: "disc", label_zh: "盘形插齿刀" },
          { variant: "bowl", variant_zh: "碗形插齿刀", variant_en: "Bowl", id: "bowl", label_zh: "碗形插齿刀" },
          { variant: "taper_shank", variant_zh: "锥柄插齿刀", variant_en: "Taper Shank", id: "taper_shank", label_zh: "锥柄插齿刀" },
          { variant: "hub", variant_zh: "筒形插齿刀", variant_en: "Hub", id: "hub", label_zh: "筒形插齿刀" },
        ],
      },
      {
        subcategory: "gear_shaving", subcategory_zh: "剃齿刀", subcategory_en: "Shaving", id: "gear_shaving", label_zh: "剃齿刀",
        variants: [
          { variant: "disc", variant_zh: "盘形剃齿刀", variant_en: "Disc", id: "disc", label_zh: "盘形剃齿刀" },
          { variant: "rack", variant_zh: "齿条形剃齿刀", variant_en: "Rack", id: "rack", label_zh: "齿条形剃齿刀" },
        ],
      },
      {
        subcategory: "gear_milling_cutter", subcategory_zh: "齿轮铣刀", subcategory_en: "Gear Milling", id: "gear_milling_cutter", label_zh: "齿轮铣刀",
        variants: [
          { variant: "disc", variant_zh: "盘形齿轮铣刀", variant_en: "Disc", id: "disc", label_zh: "盘形齿轮铣刀" },
          { variant: "finger", variant_zh: "指形齿轮铣刀", variant_en: "Finger", id: "finger", label_zh: "指形齿轮铣刀" },
        ],
      },
      {
        subcategory: "gear_bevel", subcategory_zh: "锥齿轮刀具", subcategory_en: "Bevel Gear", id: "gear_bevel", label_zh: "锥齿轮刀具",
        variants: [
          { variant: "spiral", variant_zh: "弧齿锥齿轮铣刀", variant_en: "Spiral", id: "spiral", label_zh: "弧齿锥齿轮铣刀" },
          { variant: "straight", variant_zh: "直齿锥齿轮刨刀", variant_en: "Straight", id: "straight", label_zh: "直齿锥齿轮刨刀" },
        ],
      },
    ],
  },
];
