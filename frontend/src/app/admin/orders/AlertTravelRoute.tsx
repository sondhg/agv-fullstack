import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Lightbulb } from "lucide-react";

export function AlertTravelRoute() {
  return (
    <Alert>
      <Lightbulb className="h-4 w-4" />
    <AlertTitle>Travel sequence of nodes for each order:</AlertTitle>
      <AlertDescription>
        Parking → Storage → Workstation → Parking
      </AlertDescription>
    </Alert>
  );
}
