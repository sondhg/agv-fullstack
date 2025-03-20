import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export function AccordionCSVMapGuide() {
  return (
    <Accordion type="single" collapsible className="w-full">
      <AccordionItem value="item-1">
        <AccordionTrigger>Purpose of 1st CSV</AccordionTrigger>
        <AccordionContent>
          The first CSV file should contain the connection and distance data
          between the nodes. If you download sample files, the 1st CSV file is
          named <code>map-connection-and-distance.csv</code>.
        </AccordionContent>
      </AccordionItem>
      <AccordionItem value="item-2">
        <AccordionTrigger>Purpose of 2nd CSV</AccordionTrigger>
        <AccordionContent>
          The second CSV file should contain the relative cardinal directions
          data between the nodes. If you download sample files, the 2nd CSV file
          is named <code>map-direction.csv</code>.
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
