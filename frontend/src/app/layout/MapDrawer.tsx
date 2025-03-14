import map_image from "@/assets/map_image.png";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerFooter,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { Terminal } from "lucide-react";

export function MapDrawer() {
  return (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="secondary">Show map</Button>
      </DrawerTrigger>
      <DrawerContent>
        <div className="mx-auto w-full max-w-6xl">
          <div className="columns-2 p-4 pb-0">
            <img src={map_image} alt="Map layout" />
            <div className="space-y-2">
              <Alert>
                <Terminal className="h-4 w-4" />
                <AlertTitle className="text-blue-500">Blue</AlertTitle>
                <AlertDescription>Start points</AlertDescription>
              </Alert>
              <Alert>
                <Terminal className="h-4 w-4" />
                <AlertTitle className="text-red-500">Red</AlertTitle>
                <AlertDescription>End points</AlertDescription>
              </Alert>
              <Alert>
                <Terminal className="h-4 w-4" />
                <AlertTitle className="text-yellow-500">Yellow</AlertTitle>
                <AlertDescription>Charge stations</AlertDescription>
              </Alert>
              <Alert>
                <Terminal className="h-4 w-4" />
                <AlertTitle className="text-green-500">Green</AlertTitle>
                <AlertDescription>Traverse points</AlertDescription>
              </Alert>
            </div>
          </div>
          <DrawerFooter>
            <DrawerClose asChild>
              <Button>Close (or Esc key)</Button>
            </DrawerClose>
          </DrawerFooter>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
