import {
  AGVWithAnimation,
  NodePositions,
  Position,
} from "../types/MapVisualizerTypes";

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

/**
 * Calculate the current position of an AGV during animation
 */
export function calculateAGVPosition(
  agv: AGVWithAnimation,
  positions: NodePositions,
): Position | null {
  // Skip rendering if current_node is null (AGV is not on the map)
  if (agv.current_node === null) return null;

  // Calculate the current position of the AGV based on animation progress
  if (
    agv.isAnimating &&
    agv.previousNode !== null &&
    agv.current_node !== null
  ) {
    const fromPos = positions[agv.previousNode];
    const toPos = positions[agv.current_node];

    if (!fromPos || !toPos) return null;

    // Linear interpolation between previousNode and current_node
    return {
      x: fromPos.x + (toPos.x - fromPos.x) * agv.animationProgress,
      y: fromPos.y + (toPos.y - fromPos.y) * agv.animationProgress,
    };
  } else if (positions[agv.current_node]) {
    // If not animating, use the current node position
    return positions[agv.current_node];
  }

  return null; // Position not found
}

/**
 * Calculate the rotation angle for an AGV icon based on movement direction
 */
export function calculateAGVRotation(
  agv: AGVWithAnimation,
  positions: NodePositions,
): number {
  let angle = 0;

  if (
    agv.isAnimating &&
    agv.previousNode !== null &&
    agv.current_node !== null
  ) {
    const fromPos = positions[agv.previousNode];
    const toPos = positions[agv.current_node];

    if (fromPos && toPos) {
      angle =
        Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x) * (180 / Math.PI);
    }
  }

  return angle;
}
