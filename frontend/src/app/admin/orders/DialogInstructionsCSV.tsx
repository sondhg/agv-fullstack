import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { CircleHelp, FileQuestion } from "lucide-react";

export function DialogInstructionsCSV() {
  // Function to get the current date in the format YYYY-MM-DD
  const getCurrentDate = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0"); // Ensure month is two digits
    const day = String(today.getDate()).padStart(2, "0"); // Ensure day is two digits
    return `${year}-${month}-${day}`;
  };

  // Function to calculate the start time by adding a specified number of minutes to the current time
  const getStartTime = (minutesFromNow: number) => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + minutesFromNow); // Add the specified number of minutes
    const hours = String(now.getHours()).padStart(2, "0"); // Ensure hours are two digits
    const minutes = String(now.getMinutes()).padStart(2, "0"); // Ensure minutes are two digits
    const seconds = String(now.getSeconds()).padStart(2, "0"); // Ensure seconds are two digits
    return `${hours}:${minutes}:${seconds}`;
  };

  // Function to generate and download the first CSV file (example 1 and 2)
  const handleDownloadCSVexample1and2 = () => {
    const currentDate = getCurrentDate(); // Get the current date
    const csvContent = `order_id,order_date,start_time,parking_node,storage_node,workstation_node
1,${currentDate},${getStartTime(1)},7,15,23,
2,${currentDate},${getStartTime(2)},19,11,16,
3,${currentDate},${getStartTime(3)},13,11,9,`;

    // Create a Blob object for the CSV content and trigger the download
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "orders-example-1-2.csv"; // Set the file name
    a.click(); // Trigger the download
    URL.revokeObjectURL(url); // Revoke the object URL to free memory
  };

  // Function to generate and download the second CSV file (example 3)
  const handleDownloadCSVexample3 = () => {
    const currentDate = getCurrentDate(); // Get the current date
    const csvContent = `order_id,order_date,start_time,parking_node,storage_node,workstation_node,
1,${currentDate},${getStartTime(1)},7,5,21,
2,${currentDate},${getStartTime(2)},17,10,22,
3,${currentDate},${getStartTime(3)},32,15,19,`;

    // Create a Blob object for the CSV content and trigger the download
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "orders-example-3.csv"; // Set the file name
    a.click(); // Trigger the download
    URL.revokeObjectURL(url); // Revoke the object URL to free memory
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost">
          <CircleHelp />
          CSV instructions
        </Button>
      </DialogTrigger>
      <DialogContent className="min-h-min min-w-min">
        <DialogHeader>
          <DialogTitle>How to import and export CSV?</DialogTitle>
        </DialogHeader>
        <Alert>
          <FileQuestion className="h-4 w-4" />
          <AlertTitle>Import CSV</AlertTitle>
          <AlertDescription>
            <div className="my-2 space-x-2 space-y-3">
              <span>Use a file with header row like this sample file:</span>
              <pre>
                <code>
                  order_id,order_date,start_time,parking_node,storage_node,workstation_node
                  <br />
                  1,2025-04-07,10:00:00,7,15,23,
                  <br />
                  2,2025-04-07,10:00:05,19,11,16,
                  <br />
                  3,2025-04-07,10:00:10,13,11,9,
                </code>
              </pre>
              {/* Button to download the first CSV file */}
              <Button onClick={handleDownloadCSVexample1and2}>
                Download sample orders-example-1-2.csv
              </Button>
              {/* Button to download the second CSV file */}
              <Button variant={"secondary"} onClick={handleDownloadCSVexample3}>
                Download sample orders-example-3.csv
              </Button>
            </div>
          </AlertDescription>
        </Alert>
        <Alert className="mt-4">
          <FileQuestion className="h-4 w-4" />
          <AlertTitle>Export CSV</AlertTitle>
          <AlertDescription>
            Download an "orders_exported.csv" file. The content of it is the
            data you see in the table below at the moment you click "Export CSV"
            button. If you want to see the history of orders later, exporting a
            CSV file could be a good idea.
          </AlertDescription>
        </Alert>
      </DialogContent>
    </Dialog>
  );
}
