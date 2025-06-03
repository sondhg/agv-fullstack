import { Connection } from "@/types/Map.types";
import { CANVAS_CONFIG } from "./MapVisualizerConfig";
import { AGVWithColor, NodePositions } from "./MapVisualizerTypes";

/**
 * Props for the MapAGVPaths component
 */
type MapAGVPathsProps = {
  agvs: AGVWithColor[];
  positions: NodePositions;
  connections: Connection[];
};

/**
 * Component for rendering AGV paths based on their current_node and remaining_path properties
 */
export const MapAGVPaths = ({
  agvs,
  positions,
  connections,
}: MapAGVPathsProps) => {
  if (!agvs || !positions || !connections) return null;

  // Helper function to check if two nodes are connected
  const areNodesConnected = (node1: number, node2: number) => {
    return connections.some(
      (conn) =>
        (conn.node1 === node1 && conn.node2 === node2) ||
        (conn.node1 === node2 && conn.node2 === node1),
    );
  };

  return (
    <>
      <defs>
        {" "}
        {/* Create animated pattern for path arrows */}
        <style type="text/css">
          {`
            @keyframes moveAlongPath {
              0% {
                offset-distance: 0%;
              }
              100% {
                offset-distance: 100%;
              }
            }
            .moving-arrow {
              animation-name: moveAlongPath;
              animation-duration: 3s;
              animation-timing-function: linear;
              animation-iteration-count: infinite;
              offset-rotate: auto;
            }
          `}
        </style>{" "}
        {/* Create arrow markers for each AGV color for the end of paths */}
        {agvs.map((agv) => (
          <marker
            key={`arrowhead-${agv.agv_id}`}
            id={`arrowhead-${agv.agv_id}`}
            markerWidth="4"
            markerHeight="3"
            refX="4"
            refY="1.5"
            orient="auto"
            className="tw-fill-current"
          >
            <polygon points="0 0, 4 1.5, 0 3" fill={agv.color} />
          </marker>
        ))}
      </defs>{" "}
      {agvs.map((agv) => {
        // Skip if AGV doesn't have a remaining path or it's empty
        if (!agv.remaining_path || agv.remaining_path.length === 0) {
          return null;
        }

        // Create full path including current_node and remaining_path
        const fullPath: number[] = [];

        // Add current_node if it exists and is not already the first in remaining_path
        if (
          agv.current_node !== null &&
          agv.current_node !== agv.remaining_path[0]
        ) {
          fullPath.push(agv.current_node);
        }

        // Add all nodes from remaining_path
        fullPath.push(...agv.remaining_path);

        // Skip if the full path has less than 2 nodes
        if (fullPath.length < 2) {
          return null;
        }

        // Create path segments for each part of the AGV's full path
        return fullPath.slice(0, -1).map((currentNode, index) => {
          const nextNode = fullPath[index + 1];

          // Skip if the nodes don't exist in our positions or if they're not connected
          if (
            !positions[currentNode] ||
            !positions[nextNode] ||
            !areNodesConnected(currentNode, nextNode)
          ) {
            return null;
          }
          const pos1 = positions[currentNode];
          const pos2 = positions[nextNode];

          // Calculate the direction vector from pos1 to pos2
          const dx = pos2.x - pos1.x;
          const dy = pos2.y - pos1.y;

          // Calculate the distance between the two points
          const distance = Math.sqrt(dx * dx + dy * dy);

          // Normalize the direction vector
          const nx = dx / distance;
          const ny = dy / distance; // Calculate the adjusted start and end points to account for the node radius
          // The start point is moved out from the center of the first node
          const adjustedX1 = pos1.x + nx * CANVAS_CONFIG.nodeRadius;
          const adjustedY1 = pos1.y + ny * CANVAS_CONFIG.nodeRadius;

          // The end point is moved in from the center of the second node
          const adjustedX2 = pos2.x - nx * CANVAS_CONFIG.nodeRadius;
          const adjustedY2 = pos2.y - ny * CANVAS_CONFIG.nodeRadius;

          // Create a unique path ID for this segment
          const pathId = `path-${agv.agv_id}-${index}`;

          // Calculate the total path length for consistent animation
          const pathLength = Math.sqrt(
            Math.pow(adjustedX2 - adjustedX1, 2) +
              Math.pow(adjustedY2 - adjustedY1, 2),
          );

          return (
            <g key={`agv-${agv.agv_id}-path-${index}`}>
              {/* Define the path */}
              <path
                id={pathId}
                d={`M${adjustedX1},${adjustedY1} L${adjustedX2},${adjustedY2}`}
                stroke="none"
                fill="none"
              />{" "}
              {/* Main path line */}
              <line
                x1={adjustedX1}
                y1={adjustedY1}
                x2={adjustedX2}
                y2={adjustedY2}
                stroke={agv.color}
                strokeWidth="3"
                strokeOpacity="0.9"
                strokeLinecap="round"
                markerEnd={`url(#arrowhead-${agv.agv_id})`}
              />{" "}
              {/* Single animated circle along the path */}
              <circle
                key={`arrow-${agv.agv_id}-${index}`}
                r="2.5"
                fill={agv.color}
                style={{
                  offsetPath: `path('M${adjustedX1},${adjustedY1} L${adjustedX2},${adjustedY2}')`,
                  offsetRotate: "auto",
                  animation: `moveAlongPath ${Math.max(3, pathLength / 100)}s linear infinite`,
                }}
                className="moving-arrow"
              />
            </g>
          );
        });
      })}
    </>
  );
};
