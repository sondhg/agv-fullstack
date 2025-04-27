import { CANVAS_CONFIG } from "../constants/MapVisualizerConfig";
import { NodePositions } from "../types/MapVisualizerTypes";

/**
 * Props for the MapNodes component
 */
type MapNodesProps = {
  nodes: number[];
  positions: NodePositions;
};

/**
 * Component for rendering node circles and their labels on the map
 */
export const MapNodes = ({ nodes, positions }: MapNodesProps) => {
  return (
    <>
      {/* Render node circles */}
      {nodes.map((node) => {
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
      })}

      {/* Render node labels */}
      {nodes.map((node) => {
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
      })}
    </>
  );
};
