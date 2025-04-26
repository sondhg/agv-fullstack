import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { MassDeleteButton } from "@/components/ui/mass-delete-button";
import { useTableSelection } from "@/hooks/useTableSelection";
import {
  bulkDeleteAGVs,
  deleteAGV,
  dispatchOrdersToAGVs,
  getAGVs,
} from "@/services/APIs/agvsAPI";
import { fetchMapData } from "@/services/APIs/mapAPI";
import { AGV } from "@/types/AGV.types";
import { MapData } from "@/types/Map.types";
import { CalendarPlus } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { MapVisualizer } from "../map/MapVisualizer";
import { AlgorithmSelect } from "./AlgorithmSelect";
import { columnsTableAGVs } from "./columnsTableAGVs";
import { DialogFormCreateAGVs } from "./DialogFormCreateAGVs";
import { FormSimulateUpdateAgvPosition } from "./FormSimulateUpdateAgvPosition";

export function PageAGVs() {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [listData, setListData] = useState<AGV[]>([]);
  const [mapData, setMapData] = useState<MapData | null>(null);
  const {
    rowSelection,
    setRowSelection,
    selectedIds: selectedAgvIds,
    resetSelection,
  } = useTableSelection<AGV>(listData, "agv_id");

  const fetchListData = async () => {
    const data = await getAGVs();
    setListData(data);
  };

  const handleClickBtnDelete = async (agv_id: number) => {
    try {
      await deleteAGV(agv_id);
      toast.success("Delete AGV successfully");
      await fetchListData();
    } catch (error) {
      console.error("Failed to delete AGV:", error);
      toast.error("Failed to delete AGV. Please try again.");
    }
  };

  const [isDispatching, setIsDispatching] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] =
    useState<string>("dijkstra");

  const handleDispatchOrdersToAGVs = async () => {
    try {
      setIsDispatching(true);
      await dispatchOrdersToAGVs(selectedAlgorithm);
      toast.success("Successfully dispatched orders to AGVs");
      await fetchListData();
    } catch (error) {
      if (error instanceof Response) {
        const errorData = await error.json();
        toast.error(errorData.error || "Failed to dispatch orders to AGVs");
      } else {
        toast.error("Failed to dispatch orders to AGVs");
      }
      console.error("Error dispatching orders to AGVs:", error);
    } finally {
      setIsDispatching(false);
    }
  };

  const handleShowMap = async () => {
    try {
      // Check if map data is cached
      const cachedData = localStorage.getItem("cachedMapData");
      if (cachedData) {
        const parsedData = JSON.parse(cachedData) as MapData;
        setMapData(parsedData);
        return;
      }

      // Fetch map data from backend if not cached
      const data = (await fetchMapData()) as MapData;

      if (!data || !data.nodes || !data.connections || !data.directions) {
        toast.error("Failed to load map data.");
        setMapData(null);
        return;
      }

      setMapData(data);
      // Cache the map data
      localStorage.setItem("cachedMapData", JSON.stringify(data));
    } catch (error) {
      console.error("Error fetching map data:", error);
      toast.error("Failed to load map data.");
    }
  };

  useEffect(() => {
    fetchListData();
    handleShowMap();
  }, []);

  return (
    <div className="space-y-5">
      <h2 className="text-3xl font-bold">AGVs</h2>

      <div className="flex flex-1 flex-col">
        <div className="gap-2">
          <div className="flex flex-col gap-4 md:gap-6">
            <div className="grid grid-cols-1 gap-10 xl:grid-cols-6">
              <div className="col-start-1 col-end-2 flex flex-col gap-4">
                <DialogFormCreateAGVs
                  isDialogOpen={isDialogOpen}
                  setIsDialogOpen={setIsDialogOpen}
                  fetchListData={fetchListData}
                />
                <MassDeleteButton
                  selectedIds={selectedAgvIds}
                  onDelete={bulkDeleteAGVs}
                  itemName="AGVs"
                  onSuccess={fetchListData}
                  resetSelection={resetSelection}
                />
              </div>
              <div className="col-start-3 col-end-4 flex flex-col gap-4">
                <AlgorithmSelect
                  selectedAlgorithm={selectedAlgorithm}
                  onAlgorithmChange={(value) => setSelectedAlgorithm(value)}
                />
                <Button
                  onClick={handleDispatchOrdersToAGVs}
                  disabled={isDispatching}
                  className="w-full"
                >
                  <CalendarPlus className="mr-2 h-4 w-4" />
                  {isDispatching ? "Dispatching..." : "Dispatch orders to AGVs"}
                </Button>
              </div>
              <div className="col-start-1 col-end-4">
                <FormSimulateUpdateAgvPosition
                  onUpdateSuccess={fetchListData}
                />
              </div>
            </div>
            <DataTable
              data={listData}
              columns={columnsTableAGVs(handleClickBtnDelete)}
              filterSearchByColumn="agv_id"
              onRowSelectionChange={setRowSelection}
              rowSelection={rowSelection}
            />

            {/* Map Visualization Section */}
            <div className="mt-8">
              <h3 className="mb-4 text-xl font-semibold">Map Visualization</h3>
              {mapData ? (
                <MapVisualizer data={mapData} />
              ) : (
                <div className="rounded-md border border-dashed p-6 text-center">
                  <p className="text-muted-foreground">
                    No map data available. Please make sure you've imported map
                    data in the Map section.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
