import { MapVisualizer } from "@/app/admin/map/MapVisualizer";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { fetchMapData } from "@/services/APIs/mapAPI";
import { MapData } from "@/types/Map.types";
import { useState } from "react";
import { toast } from "sonner";

interface DialogMapProps {
  mapData: MapData | null;
}

export function DialogMap() {
  const [mapData, setMapData] = useState<DialogMapProps["mapData"]>(null);

  const handleFetchMapData = async () => {
    try {
      const data = await fetchMapData() as MapData;
      console.log("Fetched map data:", data); // Debug log

      if (!data || !data.nodes || !data.connections) {
        toast.error("Failed to load map data.");
        return;
      }
      setMapData(data);
    } catch (error) {
      console.error("Error fetching map data:", error);
      toast.error("Failed to load map data.");
    }
  };

  return (
    <Dialog onOpenChange={(isOpen) => isOpen && handleFetchMapData()}>
      <DialogTrigger asChild>
        <Button variant="secondary">Show map</Button>
      </DialogTrigger>
      <DialogContent className="min-h-fit min-w-[650px]">
        <DialogHeader>
          <DialogTitle>Map layout</DialogTitle>
          <DialogDescription>
            Go to Map page if you want to edit the map layout.
          </DialogDescription>
        </DialogHeader>
        <ScrollArea className="max-h-[500px] max-w-full">
          <div className="flex items-center space-x-2">
            <div className="flex-1 gap-2">
              <div className="">
                {mapData ? (
                  <MapVisualizer data={mapData} /> // Render MapVisualizer if mapData exists
                ) : (
                  <p>Map layout not available.</p>
                )}
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
