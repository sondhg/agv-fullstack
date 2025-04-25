import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

const steps = [
  {
    title: "Login to your account.",
    description:
      "Register and login under 'Home & Auth' in the sidebar to access 'Admin' pages.",
  },
  {
    title: "Create a map layout.",
    description: "Go to Map page to create a layout if you don't have one.",
  },
  {
    title: "Create orders.",
    description:
      "Go to Orders page to create orders via form or import CSV files.",
  },
  {
    title: "Register AGVs to the system.",
    description:
      "Go to AGVs page to register AGVs with their IDs and preferred parking node.",
  },
  {
    title: "Dispatch orders to AGVs.",
    description:
      "Go to AGVs page to assign created orders to AGVs and calculate initial pathfinding parameters.",
  },
  {
    title: "Simulate AGVs movement and see data being updated.",
    description:
      "Go to AGVs page to use the 24-step simulation program and view data changes as AGVs travel.",
  },
];

type CardProps = React.ComponentProps<typeof Card>;

export function HowToUseGUIGuide({ className, ...props }: CardProps) {
  return (
    <Card className={cn("w-full", className)} {...props}>
      <CardHeader>
        <CardTitle>How to use this web app</CardTitle>
        <CardDescription>Follow the steps below.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4">
        <div>
          {steps.map((step, index) => (
            <div
              key={index}
              className="mb-4 grid grid-cols-[25px_1fr] items-start pb-4 last:mb-0 last:pb-0"
            >
              <span className="flex h-2 w-2 translate-y-1 rounded-full bg-sky-500" />
              <div className="space-y-1">
                <p className="text-sm font-medium leading-none">{step.title}</p>
                <p className="text-sm text-muted-foreground">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
