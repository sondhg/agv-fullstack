import { Connection, MapData } from "@/types/Map.types";
import { useEffect, useState } from "react";

/**
 * Position type representing a point with x and y coordinates
 */
type Position = { x: number; y: number };

/**
 * NodePositions type representing a mapping of node IDs to their positions
 */
type NodePositions = { [key: number]: Position };

/**
 * SVG Canvas configuration constants
 */
const CANVAS_CONFIG = {
  width: 1000,
  height: 1000,
  padding: 50,
  startX: 500, // Arbitrary starting x-coordinate
  startY: 500, // Arbitrary starting y-coordinate
  distanceScale: 10, // Scale factor for distances
  nodeRadius: 15,
};

/**
 * Direction constants
 */
enum DirectionEnum {
  North = 1,
  East = 2,
  South = 3,
  West = 4,
}

/**
 * MapVisualizer component for visualizing a map of nodes and connections
 */
export const MapVisualizer = ({ data }: { data: MapData }) => {
  const [scaledPositions, setScaledPositions] = useState<NodePositions>({});

  useEffect(() => {
    if (!data || !data.nodes || !data.connections) {
      console.error("Invalid data structure:", data);
      return;
    }

    // Calculate node positions
    const unscaledPositions = calculateNodePositions(data);

    // Scale positions to fit within the canvas
    const scaled = scalePositionsToFit(unscaledPositions);

    setScaledPositions(scaled);
  }, [data]);

  return (
    <div className="relative border border-gray-300 p-5">
      <svg
        viewBox={`0 0 ${CANVAS_CONFIG.width} ${CANVAS_CONFIG.height}`}
        preserveAspectRatio="xMidYMid meet"
        width="100%"
        height="auto"
        className="border border-gray-400 bg-zinc-200"
      >
        {renderConnections(data.connections, scaledPositions)}
        {renderNodes(data.nodes, scaledPositions)}
        {renderNodeLabels(data.nodes, scaledPositions)}
      </svg>
    </div>
  );
};

/**
 * Calculate positions for each node based on connections and directions
 */
function calculateNodePositions(data: MapData): NodePositions {
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
function calculatePositionFromDirection(
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
function scalePositionsToFit(positions: NodePositions): NodePositions {
  const allX = Object.values(positions).map((pos) => pos.x);
  const allY = Object.values(positions).map((pos) => pos.y);

  const minX = Math.min(...allX);
  const maxX = Math.max(...allX);
  const minY = Math.min(...allY);
  const maxY = Math.max(...allY);

  const { width, height, padding } = CANVAS_CONFIG;

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
 * Render connection lines and distance labels between nodes
 */
function renderConnections(
  connections: Connection[],
  positions: NodePositions,
) {
  return connections.map((conn, index) => {
    const pos1 = positions[conn.node1];
    const pos2 = positions[conn.node2];

    if (!pos1 || !pos2) return null;

    const { x: labelX, y: labelY } = calculateLabelPosition(pos1, pos2);

    return (
      <g key={`connection-${index}`}>
        <line
          x1={pos1.x}
          y1={pos1.y}
          x2={pos2.x}
          y2={pos2.y}
          stroke="black"
          strokeWidth="2"
        />
        <text
          x={labelX}
          y={labelY}
          textAnchor="middle"
          fontSize="12"
          fill="red"
        >
          {conn.distance}
        </text>
      </g>
    );
  });
}

/**
 * Calculate the position for a connection label based on line orientation
 */
function calculateLabelPosition(pos1: Position, pos2: Position): Position {
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
 * Render node circles on the map
 */
function renderNodes(nodes: number[], positions: NodePositions) {
  return nodes.map((node) => {
    const pos = positions[node];
    return (
      pos && (
        <circle
          key={`node-${node}`}
          cx={pos.x}
          cy={pos.y}
          r={CANVAS_CONFIG.nodeRadius}
          fill="lightblue"
          stroke="black"
        />
      )
    );
  });
}

/**
 * Render node labels (node IDs) on the map
 */
function renderNodeLabels(nodes: number[], positions: NodePositions) {
  return nodes.map((node) => {
    const pos = positions[node];
    return (
      pos && (
        <text
          key={`label-${node}`}
          x={pos.x}
          y={pos.y}
          textAnchor="middle"
          dy=".3em"
          fontSize="12"
        >
          {node}
        </text>
      )
    );
  });
}
