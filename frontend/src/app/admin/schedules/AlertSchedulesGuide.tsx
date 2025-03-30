import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";

export const AlertSchedulesGuide = () => {
  return (
    <Alert>
      <Terminal className="h-4 w-4" />
      <AlertTitle>
        Choose a path-finding algorithm in the dropdown below
      </AlertTitle>
      <AlertDescription>
        Choose either Dijkstra's algorithm or Q-Learning to generate schedules.
      </AlertDescription>
    </Alert>
  );
};
