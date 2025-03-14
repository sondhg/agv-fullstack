import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { CircleHelp } from "lucide-react";

export function DialogInstructionsCSV() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost">
          <CircleHelp />
          CSV instructions
        </Button>
      </DialogTrigger>
      <DialogContent className="min-h-[400px] min-w-[700px]">
        <DialogHeader>
          <DialogTitle>How to import and export CSV?</DialogTitle>
        </DialogHeader>
        <Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>Import CSV</AccordionTrigger>
            <AccordionContent>
              Use a file with header row like this testOrders.csv file:
              <Separator className="my-4" />
              <pre>
                <code>
                  order_id,order_date,start_time,start_point,end_point,load_name,load_amount,load_weight
                  <br />
                  1,2024-11-30,10:00:00,1,10,stone,10,10
                  <br />
                  2,2024-11-30,10:00:05,2,11,wood,10,20
                  <br />
                  3,2024-11-30,10:00:10,3,12,iron,10,30
                </code>
              </pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
        <Accordion type="single" collapsible>
          <AccordionItem value="item-2">
            <AccordionTrigger>Export CSV</AccordionTrigger>
            <AccordionContent>
              Download an "orders_exported.csv" file. The content of it is the
              data you see in the table below at the moment you click "Export
              CSV" button.
            </AccordionContent>
            <AccordionContent>
              If you want to see the history of orders later, exporting a CSV
              file could be a good idea.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </DialogContent>
    </Dialog>
  );
}
