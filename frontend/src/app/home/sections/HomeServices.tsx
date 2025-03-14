import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export function HomeServices() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Services</CardTitle>
        <CardDescription>
          Users can control AGVs and see data returned from them as they move.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger> Authentication</AccordionTrigger>
            <AccordionContent>
              Register, then login before doing anything else.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-2">
            <AccordionTrigger>Dashboard</AccordionTrigger>
            <AccordionContent>
              View live parameters such as speed, battery percentage, location,
              etc. as AGVs travel based on schedules you made.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-3">
            <AccordionTrigger>Orders</AccordionTrigger>
            <AccordionContent>
              Create orders - form inputs containing instructions for AGVs to
              operate on. Orders can be updated or removed.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-4">
            <AccordionTrigger>Schedules</AccordionTrigger>
            <AccordionContent>
              View schedules generated through algorithms and orders you made.
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-5">
            <AccordionTrigger>AGVs team</AccordionTrigger>
            <AccordionContent>
              Add or remove AGVs from a team of maximum 4 AGVs.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  );
}
