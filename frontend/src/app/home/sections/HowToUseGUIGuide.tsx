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
    description: "Go to the Map page to create a layout if you don't have one.",
  },
  {
    title: "Create orders.",
    description:
      "Use the Orders page to create orders via form or import CSV files.",
  },
  {
    title: "Generate schedules.",
    description:
      "Generate schedules from orders created, based on algorithms, on the Schedules page. Schedules are then assigned to AGVs.",
  },
  {
    title: "View real-time AGV data.",
    description:
      "Check live data returned by AGVs on the Dashboard page as they travel based on schedules.",
  },
];

type CardProps = React.ComponentProps<typeof Card>;

export function HowToUseGUIGuide({ className, ...props }: CardProps) {
  return (
    <Card className={cn("w-full", className)} {...props}>
      <CardHeader>
        <CardTitle>How to use this web app</CardTitle>
        <CardDescription>
          Follow the steps below.
        </CardDescription>
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
                <p className="text-sm font-medium leading-none">
                  {step.title}
                </p>
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
