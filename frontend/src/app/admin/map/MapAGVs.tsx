import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Forklift } from "lucide-react";
import { CANVAS_CONFIG } from "./MapVisualizerConfig";
import { AGVWithColor, NodePositions } from "./MapVisualizerTypes";

/**
 * Props for the MapAGVs component
 */
type MapAGVsProps = {
  agvs: AGVWithColor[];
  positions: NodePositions;
};

/**
 * Component for rendering AGVs as Forklift icons
 */
export const MapAGVs = ({ agvs, positions }: MapAGVsProps) => {
  return (
    <>
      {agvs.map((agv) => {
        // Skip rendering if AGV is not on the map
        if (agv.current_node === null || !positions[agv.current_node])
          return null;

        // Get the AGV position from its current node
        const position = positions[agv.current_node];

        // Size adjustment for the Forklift icon
        const iconSize = CANVAS_CONFIG.agvSize;

        return (
          <TooltipProvider key={`agv-${agv.agv_id}`} delayDuration={0}>
            <Tooltip>
              <TooltipTrigger asChild>
                <g
                  transform={`translate(${position.x - iconSize / 2}, ${position.y - iconSize / 2})`}
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
                  <Forklift
                    size={iconSize}
                    color={agv.color}
                    fill={agv.color}
                    fillOpacity={0.3}
                    className="cursor-pointer"
                  />
                </g>
              </TooltipTrigger>
              <TooltipContent>
                <p>AGV {agv.agv_id}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        );
      })}
    </>
  );
};
