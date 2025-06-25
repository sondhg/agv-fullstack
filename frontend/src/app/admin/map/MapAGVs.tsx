import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  Circle,
  Forklift,
  HelpCircle,
  MapPin,
  RotateCcw,
  Slash,
} from "lucide-react";
import { useState } from "react";
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
  // State to manage tooltip visibility for each AGV (track hidden ones instead of visible ones)
  const [hiddenTooltips, setHiddenTooltips] = useState<Set<number>>(new Set());

  const toggleTooltip = (agvId: number) => {
    setHiddenTooltips((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(agvId)) {
        newSet.delete(agvId); // Show tooltip
      } else {
        newSet.add(agvId); // Hide tooltip
      }
      return newSet;
    });
  };

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
            <Tooltip
              open={!hiddenTooltips.has(agv.agv_id)}
              onOpenChange={() => {}} // Prevent automatic open/close on hover
            >
              <TooltipTrigger asChild>
                <g
                  transform={`translate(${position.x - iconSize / 2}, ${position.y - iconSize / 2})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleTooltip(agv.agv_id);
                  }}
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
                  <div className="flex items-center gap-2">
                    <Circle
                      size={16}
                      className={
                        agv.motion_state === 0
                          ? "fill-yellow-500 text-yellow-500" // Idle
                          : agv.motion_state === 1
                            ? "fill-green-500 text-green-500" // Moving
                            : "fill-red-500 text-red-500" // Waiting
                      }
                    />
                    <span>
                      {agv.motion_state === 0
                        ? "Idle"
                        : agv.motion_state === 1
                          ? "Moving"
                          : "Waiting"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {agv.direction_change !== null ? (
                      agv.direction_change === 0 ? (
                        <ArrowUp size={16} />
                      ) : agv.direction_change === 1 ? (
                        <RotateCcw size={16} />
                      ) : agv.direction_change === 2 ? (
                        <ArrowLeft size={16} />
                      ) : agv.direction_change === 3 ? (
                        <ArrowRight size={16} />
                      ) : (
                        <HelpCircle size={16} />
                      )
                    ) : (
                      <Slash size={16} />
                    )}
                    <span>
                      {agv.direction_change !== null
                        ? agv.direction_change === 0
                          ? "Straight"
                          : agv.direction_change === 1
                            ? "Turn around"
                            : agv.direction_change === 2
                              ? "Left"
                              : agv.direction_change === 3
                                ? "Right"
                                : "Unknown"
                        : "N/A"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin size={16} />
                    <span>{agv.reserved_node ?? "N/A"}</span>
                  </div>
                </div>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        );
      })}
    </>
  );
};
