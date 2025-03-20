import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { FileQuestion } from "lucide-react";

export function AlertMapGuide() {
  return (
    <Alert>
      <FileQuestion className="h-4 w-4" />
      <AlertTitle>Map creation guide</AlertTitle>
      <AlertDescription>
        You must import 2 CSV files to create a map layout. These will be
        referred to as the <strong>1st and 2nd CSV files</strong>. They are{" "}
        <strong>
          <u>different</u>
        </strong>{" "}
        from each other, and their contents are explained below.
      </AlertDescription>
    </Alert>
  );
}
