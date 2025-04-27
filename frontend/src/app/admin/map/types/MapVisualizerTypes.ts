import { AGV } from "@/types/AGV.types";
import { MapData } from "@/types/Map.types";

/**
 * Position type representing a point with x and y coordinates
 */
export type Position = { x: number; y: number };

/**
 * NodePositions type representing a mapping of node IDs to their positions
 */
export type NodePositions = { [key: number]: Position };

/**
 * Type representing an AGV with animation state
 */
export type AGVWithAnimation = AGV & {
  color: string;
  previousNode: number | null;
  animationProgress: number;
  isAnimating: boolean;
};

/**
 * Props for the MapVisualizer component
 */
export type MapVisualizerProps = {
  data: MapData;
  agvs?: AGV[];
};
