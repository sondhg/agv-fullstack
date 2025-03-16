import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { FileQuestion } from "lucide-react";

export function AlertMapGuide() {
  return (
    <Alert>
      <FileQuestion className="h-4 w-4" />
      <AlertTitle>Map creation guide</AlertTitle>
      <AlertDescription>
        You must import 2 CSV files to create a map layout. Test files can be found in <code>sample-data</code> folder.
      </AlertDescription>
    </Alert>
  );
}
