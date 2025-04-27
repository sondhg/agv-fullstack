import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Car } from "lucide-react";
import { CANVAS_CONFIG } from "../constants/MapVisualizerConfig";
import { AGVWithAnimation, NodePositions } from "../types/MapVisualizerTypes";
import {
  calculateAGVPosition,
  calculateAGVRotation,
} from "../utils/MapRenderingUtils";

/**
 * Props for the MapAGVs component
 */
type MapAGVsProps = {
  agvs: AGVWithAnimation[];
  positions: NodePositions;
};

/**
 * Component for rendering AGVs as Car icons with animation between nodes
 */
export const MapAGVs = ({ agvs, positions }: MapAGVsProps) => {
  return (
    <>
      {agvs.map((agv) => {
        // Get the AGV position
        const position = calculateAGVPosition(agv, positions);
        if (!position) return null;

        // Calculate the angle of rotation for the Car icon
        const angle = calculateAGVRotation(agv, positions);

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
