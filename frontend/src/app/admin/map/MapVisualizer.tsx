import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Connection, MapData } from "@/types/Map.types";
import { useEffect, useState, useRef } from "react";
import { Car } from "lucide-react";
import { AGV } from "@/types/AGV.types";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

/**
 * Position type representing a point with x and y coordinates
 */
type Position = { x: number; y: number };

/**
 * NodePositions type representing a mapping of node IDs to their positions
 */
type NodePositions = { [key: number]: Position };

/**
 * Type representing an AGV with animation state
 */
type AGVWithAnimation = AGV & {
  color: string;
  previousNode: number | null;
  animationProgress: number;
  isAnimating: boolean;
};

/**
 * SVG Canvas configuration constants
 */
const CANVAS_CONFIG = {
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
enum DirectionEnum {
  North = 1,
  East = 2,
  South = 3,
  West = 4,
}

// Array of colors for AGVs
const AGV_COLORS = [
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

/**
 * MapVisualizer component for visualizing a map of nodes and connections
 */
export const MapVisualizer = ({
  data,
  agvs = [],
}: {
  data: MapData;
  agvs?: AGV[];
}) => {
  const [scaledPositions, setScaledPositions] = useState<NodePositions>({});
  const [canvasDimensions, setCanvasDimensions] = useState({
    width: CANVAS_CONFIG.defaultWidth,
    height: CANVAS_CONFIG.defaultHeight,
  });
  const [agvsState, setAgvsState] = useState<AGVWithAnimation[]>([]);
  const animationFrameRef = useRef<number | null>(null);
  const lastAnimationTimeRef = useRef<number | null>(null);

  // Initialize AGVs with colors and animation state
  useEffect(() => {
    const updatedAgvs = agvs.map((agv, index) => ({
      ...agv,
      color: AGV_COLORS[index % AGV_COLORS.length],
      previousNode: agv.current_node,
      animationProgress: 0,
      isAnimating: false,
    }));
    setAgvsState(updatedAgvs);
  }, [agvs]);

  // Calculate node positions
  useEffect(() => {
    if (!data || !data.nodes || !data.connections) {
      console.error("Invalid data structure:", data);
      return;
    }

    const unscaledPositions = calculateNodePositions(data);
    const dimensions = calculateCanvasDimensions(unscaledPositions);
    setCanvasDimensions(dimensions);
    const scaled = scalePositionsToFit(unscaledPositions, dimensions);
    setScaledPositions(scaled);
  }, [data]);

  // Animation update function
  const updateAnimation = (timestamp: number) => {
    if (!lastAnimationTimeRef.current) {
      lastAnimationTimeRef.current = timestamp;
    }

    const deltaTime = timestamp - lastAnimationTimeRef.current;
    lastAnimationTimeRef.current = timestamp;

    // Update animation progress for each AGV
    let needsAnimation = false;

    setAgvsState((prevAgvs) =>
      prevAgvs.map((agv) => {
        if (!agv.isAnimating) return agv;

        const newProgress =
          agv.animationProgress +
          deltaTime / CANVAS_CONFIG.agvAnimationDuration;

        if (newProgress >= 1) {
          // Animation completed
          return {
            ...agv,
            animationProgress: 1,
            isAnimating: false,
            previousNode: agv.current_node,
          };
        } else {
          needsAnimation = true;
          return {
            ...agv,
            animationProgress: newProgress,
          };
        }
      }),
    );

    // Continue the animation loop if needed
    if (needsAnimation) {
      animationFrameRef.current = requestAnimationFrame(updateAnimation);
    } else {
      animationFrameRef.current = null;
      lastAnimationTimeRef.current = null;
    }
  };

  // Start or stop animation as needed
  useEffect(() => {
    // Function to check if any AGVs need animation and start the animation loop
    const checkAndStartAnimation = () => {
      if (
        agvsState.some((agv) => agv.isAnimating) &&
        !animationFrameRef.current
      ) {
        // Start animation loop
        animationFrameRef.current = requestAnimationFrame(updateAnimation);
      }
    };

    // Initial check for animations
    checkAndStartAnimation();

    // We also need to monitor for AGVs that start animating
    const animationObserver = setInterval(() => {
      if (
        agvsState.some((agv) => agv.isAnimating) &&
        !animationFrameRef.current
      ) {
        animationFrameRef.current = requestAnimationFrame(updateAnimation);
      }
    }, 100); // Check every 100ms

    return () => {
      // Cleanup animation and interval on component unmount
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      clearInterval(animationObserver);
    };
  }); // Empty dependency array since we handle state checks internally

  // Check for AGV position changes and start animations
  useEffect(() => {
    setAgvsState((prevAgvs) => {
      return prevAgvs.map((agvState) => {
        // Find the corresponding updated AGV
        const updatedAgv = agvs.find((agv) => agv.agv_id === agvState.agv_id);

        if (!updatedAgv) return agvState;

        // If current_node is null, this AGV should be removed from the map
        if (updatedAgv.current_node === null) {
          return { ...agvState, current_node: null };
        }

        // Check if position has changed
        if (
          updatedAgv.current_node !== agvState.previousNode &&
          updatedAgv.current_node !== null &&
          agvState.previousNode !== null
        ) {
          // Start animation from previous node to current node
          return {
            ...agvState,
            ...updatedAgv,
            previousNode: agvState.previousNode,
            animationProgress: 0,
            isAnimating: true,
          };
        }

        return { ...agvState, ...updatedAgv };
      });
    });
  }, [agvs]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Map Visualizer</CardTitle>
      </CardHeader>
      <CardContent>
        <svg
          viewBox={`0 0 ${canvasDimensions.width} ${canvasDimensions.height}`}
          preserveAspectRatio="xMidYMid meet"
          width="100%"
          height="auto"
          className="border border-gray-400 bg-zinc-200"
        >
          {renderConnections(data.connections, scaledPositions)}
          {renderNodes(data.nodes, scaledPositions)}
          {renderNodeLabels(data.nodes, scaledPositions)}
          {renderAGVs(agvsState, scaledPositions)}
        </svg>
      </CardContent>
    </Card>
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
function scalePositionsToFit(
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
function calculateCanvasDimensions(positions: NodePositions) {
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
  // For sparse maps with few nodes but large distances, use the actual content size
  // For dense maps with many nodes, ensure enough space per node
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

/**
 * Render AGVs as Car icons with animation between nodes
 */
function renderAGVs(agvs: AGVWithAnimation[], positions: NodePositions) {
  return agvs.map((agv) => {
    // Skip rendering if current_node is null (AGV is not on the map)
    if (agv.current_node === null) return null;

    let position: Position;

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
      position = {
        x: fromPos.x + (toPos.x - fromPos.x) * agv.animationProgress,
        y: fromPos.y + (toPos.y - fromPos.y) * agv.animationProgress,
      };
    } else if (positions[agv.current_node]) {
      // If not animating, use the current node position
      position = positions[agv.current_node];
    } else {
      return null; // Position not found
    }

    // Calculate the angle of rotation for the Car icon
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
          Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x) *
          (180 / Math.PI);
      }
    }

    // Size adjustment for the Car icon
    const iconSize = CANVAS_CONFIG.agvSize;

    return (
      <TooltipProvider key={`agv-${agv.agv_id}`} delayDuration={0}>
        <Tooltip>
          <TooltipTrigger asChild>
            <g
              transform={`translate(${position.x - iconSize / 2}, ${position.y - iconSize / 2}) rotate(${angle}, ${iconSize / 2}, ${iconSize / 2})`}
            >
              {/* Invisible larger hitbox for better tooltip triggering */}
              <rect
                x="-10"
                y="-10"
                width={iconSize + 20}
                height={iconSize + 20}
                fill="transparent"
                className="cursor-pointer"
              />
              <Car
                size={iconSize}
                color={agv.color}
                fill={agv.color}
                fillOpacity={0.3}
                className="cursor-pointer" // Add cursor-pointer to the Car icon itself
              />
            </g>
          </TooltipTrigger>
          <TooltipContent>
            <p>AGV {agv.agv_id}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  });
}
