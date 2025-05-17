import { MapData } from "@/types/Map.types";
import { CANVAS_CONFIG, DirectionEnum } from "../MapVisualizerConfig";
import { NodePositions, Position } from "../MapVisualizerTypes";

/**
 * Calculate positions for each node based on connections and directions
 */
export function calculateNodePositions(data: MapData): NodePositions {
  const positions: NodePositions = {};
  const visitedNodes = new Set<number>();
  const queue: { node: number; x: number; y: number }[] = [];

  // Start with first node at the center position
  const startNode = data.nodes[0];
  queue.push({
    node: startNode,
    x: CANVAS_CONFIG.startX,
    y: CANVAS_CONFIG.startY,
  });
  positions[startNode] = { x: CANVAS_CONFIG.startX, y: CANVAS_CONFIG.startY };

  while (queue.length > 0) {
    const { node, x, y } = queue.shift()!;
    visitedNodes.add(node);

    // Find all connections for the current node
    data.connections
      .filter((conn) => conn.node1 === node || conn.node2 === node)
      .forEach((conn) => {
        const neighbor = conn.node1 === node ? conn.node2 : conn.node1;

        if (!visitedNodes.has(neighbor)) {
          const distance = conn.distance * CANVAS_CONFIG.distanceScale;

          // Find direction from current node to neighbor
          const directionData = data.directions.find(
            (dir) => dir.node1 === node && dir.node2 === neighbor,
          );

          if (!directionData) {
            console.error(
              `Direction not found for nodes ${node} -> ${neighbor}`,
            );
            return;
          }

          // Calculate new position based on direction
          const newPosition = calculatePositionFromDirection(
            x,
            y,
            distance,
            directionData.direction,
          );

          positions[neighbor] = newPosition;
          queue.push({ node: neighbor, x: newPosition.x, y: newPosition.y });
        }
      });
  }

  return positions;
}

/**
 * Calculate a new position based on a starting position, distance, and direction
 */
export function calculatePositionFromDirection(
  x: number,
  y: number,
  distance: number,
  direction: number,
): Position {
  let newX = x;
  let newY = y;

  switch (direction) {
    case DirectionEnum.North:
      newY = y - distance;
      break;
    case DirectionEnum.East:
      newX = x + distance;
      break;
    case DirectionEnum.South:
      newY = y + distance;
      break;
    case DirectionEnum.West:
      newX = x - distance;
      break;
    default:
      console.error(`Invalid direction ${direction}`);
  }

  return { x: newX, y: newY };
}

/**
 * Scale node positions to fit within the SVG canvas
 */
export function scalePositionsToFit(
  positions: NodePositions,
  dimensions: { width: number; height: number },
): NodePositions {
  const allX = Object.values(positions).map((pos) => pos.x);
  const allY = Object.values(positions).map((pos) => pos.y);

  const minX = Math.min(...allX);
  const maxX = Math.max(...allX);
  const minY = Math.min(...allY);
  const maxY = Math.max(...allY);

  const { padding } = CANVAS_CONFIG;
  const { width, height } = dimensions;

  // Calculate scaling factors to fit the map within the canvas
  const scaleX = (width - 2 * padding) / (maxX - minX || 1);
  const scaleY = (height - 2 * padding) / (maxY - minY || 1);
  const scale = Math.min(scaleX, scaleY); // Maintain aspect ratio

  // Apply scaling to all positions
  return Object.fromEntries(
    Object.entries(positions).map(([node, pos]) => [
      node,
      {
        x: padding + (pos.x - minX) * scale,
        y: padding + (pos.y - minY) * scale,
      },
    ]),
  );
}

/**
 * Calculate appropriate canvas dimensions based on node positions
 */
export function calculateCanvasDimensions(positions: NodePositions) {
  const allX = Object.values(positions).map((pos) => pos.x);
  const allY = Object.values(positions).map((pos) => pos.y);

  // If we don't have any positions, return default dimensions
  if (allX.length === 0 || allY.length === 0) {
    return {
      width: CANVAS_CONFIG.defaultWidth,
      height: CANVAS_CONFIG.defaultHeight,
    };
  }

  const minX = Math.min(...allX);
  const maxX = Math.max(...allX);
  const minY = Math.min(...allY);
  const maxY = Math.max(...allY);

  // Calculate the content size
  const nodeCount = Object.keys(positions).length;
  const { padding, nodeRadius, nodeSizeMultiplier } = CANVAS_CONFIG;

  // Calculate dimensions based on content
  const contentWidth = Math.max(
    maxX - minX + nodeRadius * 4,
    Math.sqrt(nodeCount) * nodeRadius * nodeSizeMultiplier,
  );
  const contentHeight = Math.max(
    maxY - minY + nodeRadius * 4,
    Math.sqrt(nodeCount) * nodeRadius * nodeSizeMultiplier,
  );

  // Add padding to content size
  let width = contentWidth + 2 * padding;
  let height = contentHeight + 2 * padding;

  // Ensure the dimensions are at least the default size
  width = Math.max(width, CANVAS_CONFIG.defaultWidth);
  height = Math.max(height, CANVAS_CONFIG.defaultHeight);

  // Ensure the aspect ratio is reasonable (not too wide or too tall)
  const aspectRatio = width / height;

  if (aspectRatio > CANVAS_CONFIG.aspectRatioMax) {
    // Too wide, adjust height
    height = width / CANVAS_CONFIG.aspectRatioMax;
  } else if (aspectRatio < CANVAS_CONFIG.aspectRatioMin) {
    // Too tall, adjust width
    width = height * CANVAS_CONFIG.aspectRatioMin;
  }

  return { width, height };
}
