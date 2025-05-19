import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useEffect, useState } from "react";
import { MapAGVPaths } from "./MapAGVPaths";
import { MapAGVs } from "./MapAGVs";
import { MapConnections } from "./MapConnections";
import { MapLegend } from "./MapLegend";
import { MapNodes } from "./MapNodes";
import {
  calculateCanvasDimensions,
  calculateNodePositions,
  scalePositionsToFit,
} from "./MapPositioningUtils";
import { AGV_COLORS, CANVAS_CONFIG } from "./MapVisualizerConfig";
import {
  AGVWithColor,
  MapVisualizerProps,
  NodePositions,
} from "./MapVisualizerTypes";

/**
 * MapVisualizer component for visualizing a map of nodes and connections
 */
export const MapVisualizer = ({ data, agvs = [] }: MapVisualizerProps) => {
  const [scaledPositions, setScaledPositions] = useState<NodePositions>({});
  const [canvasDimensions, setCanvasDimensions] = useState({
    width: CANVAS_CONFIG.defaultWidth,
    height: CANVAS_CONFIG.defaultHeight,
  });
  const [agvsState, setAgvsState] = useState<AGVWithColor[]>([]);

  // Initialize AGVs with colors only
  useEffect(() => {
    const updatedAgvs = agvs.map((agv, index) => ({
      ...agv,
      color: AGV_COLORS[index % AGV_COLORS.length],
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

  return (
    <Card>
      <CardHeader>
        <CardTitle>Map Visualizer</CardTitle>
      </CardHeader>
      <CardContent>
        {" "}
        <svg
          viewBox={`0 0 ${canvasDimensions.width} ${canvasDimensions.height}`}
          preserveAspectRatio="xMidYMid meet"
          width="100%"
          height="auto"
          className="border border-gray-400 bg-zinc-200"
        >
          {/* Order matters for z-index in SVG - later elements appear on top */}
          <MapConnections
            connections={data.connections}
            positions={scaledPositions}
          />
          <MapAGVPaths
            agvs={agvsState}
            positions={scaledPositions}
            connections={data.connections}
          />{" "}
          <MapNodes nodes={data.nodes} positions={scaledPositions} />
          <MapAGVs agvs={agvsState} positions={scaledPositions} />
        </svg>
        <MapLegend />
      </CardContent>
    </Card>
  );
};
