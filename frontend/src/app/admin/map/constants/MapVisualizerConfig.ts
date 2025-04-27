/**
 * SVG Canvas configuration constants for map visualization
 */
export const CANVAS_CONFIG = {
  padding: 50,
  startX: 500, // Arbitrary starting x-coordinate
  startY: 500, // Arbitrary starting y-coordinate
  distanceScale: 10, // Scale factor for distances
  nodeRadius: 15,
  defaultWidth: 1000, // Default width for good visibility
  defaultHeight: 300, // Default height for good visibility
  nodeSizeMultiplier: 2, // Multiplier to ensure nodes have enough space
  aspectRatioMax: 2, // Maximum aspect ratio to prevent extreme rectangles
  aspectRatioMin: 0.5, // Minimum aspect ratio to prevent extreme rectangles
  agvSize: 24, // Size of the AGV icon
  agvAnimationDuration: 2000, // Animation duration in milliseconds (now 2 seconds)
  curvePathOffset: 0.2, // Curve offset for animation path (percentage of path length)
};

/**
 * Direction constants
 */
export enum DirectionEnum {
  North = 1,
  East = 2,
  South = 3,
  West = 4,
}

// Array of colors for AGVs
export const AGV_COLORS = [
  "#ef4444", // Red
  "#3b82f6", // Blue
  "#22c55e", // Green
  "#f59e0b", // Amber
  "#8b5cf6", // Violet
  "#ec4899", // Pink
  "#06b6d4", // Cyan
  "#14b8a6", // Teal
  "#f43f5e", // Rose
  "#d946ef", // Fuchsia
];
