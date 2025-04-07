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
  const handleDownloadCSVexample1and2 = () => {
    const csvContent = `order_id,order_date,start_time,parking_node,storage_node,workstation_node
1,2025-11-30,10:00:00,7,15,23,
2,2025-11-30,10:00:05,19,11,16,
3,2025-11-30,10:00:10,13,11,9,`;

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "orders-example-1-2.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadCSVexample3 = () => {
    const csvContent = `order_id,order_date,start_time,parking_node,storage_node,workstation_node,
1,2025-11-30,10:00:00,7,5,21,
2,2025-11-30,10:00:05,17,10,22,
3,2025-11-30,10:00:10,32,15,19,`;

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "orders-example-3.csv";
    a.click();
    URL.revokeObjectURL(url);
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
                  1,2025-11-30,10:00:00,7,15,23,
                  <br />
                  2,2025-11-30,10:00:05,19,11,16,
                  <br />
                  3,2025-11-30,10:00:10,13,11,9,
                </code>
              </pre>
              <Button onClick={handleDownloadCSVexample1and2}>
                Download sample orders-example-1-2.csv
              </Button>
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
