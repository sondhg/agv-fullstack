import { Position } from "./MapVisualizerTypes";

/**
 * Calculate the position for a connection label based on line orientation
 */
export function calculateLabelPosition(
  pos1: Position,
  pos2: Position,
): Position {
  // Calculate the midpoint of the line
  const midX = (pos1.x + pos2.x) / 2;
  const midY = (pos1.y + pos2.y) / 2;

  // Determine the orientation of the line
  const isHorizontal = Math.abs(pos1.y - pos2.y) < Math.abs(pos1.x - pos2.x);
  const isVertical = Math.abs(pos1.x - pos2.x) < Math.abs(pos1.y - pos2.y);

  // Adjust the offset based on the orientation
  const offsetX = isVertical ? 10 : 0; // Offset horizontally for vertical lines
  const offsetY = isHorizontal ? -10 : isVertical ? 0 : -10; // Offset vertically for horizontal/diagonal lines

  return {
    x: midX + offsetX,
    y: midY + offsetY,
  };
}
