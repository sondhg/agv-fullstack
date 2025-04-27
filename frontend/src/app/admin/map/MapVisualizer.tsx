import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useEffect, useRef, useState } from "react";
import { MapAGVs } from "./components/MapAGVs";
import { MapConnections } from "./components/MapConnections";
import { MapNodes } from "./components/MapNodes";
import { AGV_COLORS, CANVAS_CONFIG } from "./constants/MapVisualizerConfig";
import {
  AGVWithAnimation,
  MapVisualizerProps,
  NodePositions,
} from "./types/MapVisualizerTypes";
import {
  calculateCanvasDimensions,
  calculateNodePositions,
  scalePositionsToFit,
} from "./utils/MapPositioningUtils";

/**
 * MapVisualizer component for visualizing a map of nodes and connections
 */
export const MapVisualizer = ({ data, agvs = [] }: MapVisualizerProps) => {
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
          <MapConnections
            connections={data.connections}
            positions={scaledPositions}
          />
          <MapNodes nodes={data.nodes} positions={scaledPositions} />
          <MapAGVs agvs={agvsState} positions={scaledPositions} />
        </svg>
      </CardContent>
    </Card>
  );
};
