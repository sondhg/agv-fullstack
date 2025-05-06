import { SidebarTrigger } from "@/components/ui/sidebar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type Side = "top" | "right" | "bottom" | "left";

interface SidebarTriggerWithTooltipProps {
  side?: Side;
}

export function SidebarTriggerWithTooltip({
  side = "right",
}: SidebarTriggerWithTooltipProps) {
  return (
    <TooltipProvider delayDuration={0}>
      <Tooltip>
        <TooltipTrigger asChild>
          <SidebarTrigger />
        </TooltipTrigger>
        <TooltipContent side={side}>
          <span>Toggle sidebar &nbsp;</span>
          <span>
            <kbd>
              <span className="text-xs">⌘</span>B
            </kbd>
          </span>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
