import { MapVisualizer } from "@/app/admin/map/PageMap"; // Import MapVisualizer
import map_image from "@/assets/map_image.png";
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerFooter,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { fetchMapData } from "@/services/APIs/mapAPI"; // Import the fetchMapData function
import { useState } from "react";
import { toast } from "sonner";

interface MapDrawerProps {
  mapData: {
    nodes: number[];
    connections: { node1: number; node2: number; distance: number }[];
    directions: { node1: number; node2: number; direction: number }[];
  } | null;
}

export function MapDrawer() {
  const [mapData, setMapData] = useState<MapDrawerProps["mapData"]>(null);

  const handleFetchMapData = async () => {
    const data = await fetchMapData();
    console.log("Fetched map data:", data); // Debug log

    if (!data || !data.nodes || !data.connections) {
      toast.error("Failed to load map data.");
      return;
    }
    setMapData(data);
  };

  return (
    <Drawer onOpenChange={(isOpen) => isOpen && handleFetchMapData()}>
      <DrawerTrigger asChild>
        <Button variant="secondary">Show map</Button>
      </DrawerTrigger>
      <DrawerContent>
        <div className="mx-auto w-full max-w-6xl">
          <div className="p-4 pb-0">
            <div className="flex items-center justify-center space-x-2">
              {mapData ? (
                <MapVisualizer data={mapData} /> // Render MapVisualizer if mapData exists
              ) : (
                <img src={map_image} alt="Map layout" />
              )}
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
