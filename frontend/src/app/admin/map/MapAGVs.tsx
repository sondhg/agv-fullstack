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
                  />{" "}
                  <Forklift
                    size={iconSize}
                    color={agv.color}
                    fill={agv.color}
                    fillOpacity={0.3}
                    className="cursor-pointer"
                  />{" "}
                  {/* Motion state indicator */}{" "}
                  <circle
                    cx={iconSize}
                    cy={iconSize}
                    r={iconSize / 4}
                    className={
                      agv.motion_state === 0
                        ? "fill-yellow-500" // Idle - Yellow
                        : agv.motion_state === 1
                          ? "fill-green-500" // Moving - Green
                          : "fill-red-500" // Waiting - Red
                    }
                    stroke="white"
                    strokeWidth="1"
                  />
                </g>
              </TooltipTrigger>{" "}
              <TooltipContent className="max-w-xs border-none bg-slate-800 p-3 text-white">
                <p className="text-center text-lg font-bold">
                  AGV {agv.agv_id}
                </p>
                <div className="mt-1 space-y-1 text-sm">
                  <p>
                    <span className="font-medium">Motion state:</span>{" "}
                    {agv.motion_state === 0
                      ? "Idle"
                      : agv.motion_state === 1
                        ? "Moving"
                        : "Waiting"}
                  </p>
                  <p>
                    <span className="font-medium">Current Node:</span>{" "}
                    {agv.current_node !== null ? agv.current_node : "N/A"}
                  </p>
                  <p>
                    <span className="font-medium">Next Node:</span>{" "}
                    {agv.next_node !== null ? agv.next_node : "N/A"}
                  </p>
                  {agv.remaining_path && agv.remaining_path.length > 0 && (
                    <p>
                      <span className="font-medium">Remaining Path:</span>{" "}
                      {agv.remaining_path.join(" → ")}
                    </p>
                  )}
                </div>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        );
      })}
    </>
  );
};
