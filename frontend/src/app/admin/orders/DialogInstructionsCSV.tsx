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
  const handleDownloadCSV = () => {
    const csvContent = `order_id,order_date,start_time,parking_node,storage_node,workstation_node
1,2024-11-30,10:00:00,1,2,3
2,2024-11-30,10:00:05,4,5,6
3,2024-11-30,10:00:10,7,8,9`;

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "testOrders.csv";
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
            <div className="my-2 space-y-3">
              <span>
                Use a file with header row like this sample testOrders.csv file:
              </span>
              <pre>
                <code>
                  order_id,order_date,start_time,parking_node,storage_node,workstation_node
                  <br />
                  1,2024-11-30,10:00:00,1,2,3
                  <br />
                  2,2024-11-30,10:00:05,4,5,6
                  <br />
                  3,2024-11-30,10:00:10,7,8,9
                </code>
              </pre>
              <Button onClick={handleDownloadCSV}>
                Download sample testOrders.csv
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
