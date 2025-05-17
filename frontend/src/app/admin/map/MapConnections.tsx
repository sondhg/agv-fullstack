import { Connection } from "@/types/Map.types";
import { calculateLabelPosition } from "./MapRenderingUtils";
import { NodePositions } from "./MapVisualizerTypes";

/**
 * Props for the MapConnections component
 */
type MapConnectionsProps = {
  connections: Connection[];
  positions: NodePositions;
};

/**
 * Component for rendering connection lines and distance labels between nodes
 */
export const MapConnections = ({
  connections,
  positions,
}: MapConnectionsProps) => {
  return (
    <>
      {connections.map((conn, index) => {
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
      })}
    </>
  );
};
