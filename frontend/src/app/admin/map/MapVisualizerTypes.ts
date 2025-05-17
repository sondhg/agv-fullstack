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
 * Type for AGV with color property
 */
export type AGVWithColor = AGV & { color: string };

/**
 * Props for the MapVisualizer component
 */
export type MapVisualizerProps = {
  data: MapData;
  agvs?: AGV[];
};
