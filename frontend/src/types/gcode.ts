export interface GCodeSuggestion {
  operation: string;
  gcode_lines: string[];
  gcode_text: string;
  description: string;
  spindle_rpm: number;
  feed_rate: number;
  parameters_used: Record<string, number>;
  warnings: string[];
}
