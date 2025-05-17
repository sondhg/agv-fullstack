import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { MassDeleteButton } from "@/components/ui/mass-delete-button";
import { Separator } from "@/components/ui/separator";
import { CACHED_MAP_DATA_KEY } from "@/constants/localStorageKeys";
import { WS_URL } from "@/constants/websocketConstants";
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
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { MapVisualizer } from "../map/MapVisualizer";
import { AlgorithmSelect } from "./AlgorithmSelect";
import { columns1 } from "./columns1";
import { columns2 } from "./columns2";
import { DialogFormCreateAGVs } from "./DialogFormCreateAGVs";

export function PageAGVs() {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [listData, setListData] = useState<AGV[]>([]);
  const [mapData, setMapData] = useState<MapData | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Add state to track if orders have been dispatched

  const {
    rowSelection,
    setRowSelection,
    selectedIds: selectedAgvIds,
    resetSelection,
  } = useTableSelection<AGV>(listData, "agv_id");

  // Reference to track last known positions
  const lastKnownPositions = useRef<Map<number, number | null>>(new Map());

  const fetchListData = async () => {
    const data = await getAGVs();

    // Update the list data
    setListData(data);

    // Track position changes for animation
    data.forEach((agv) => {
      const lastPosition = lastKnownPositions.current.get(agv.agv_id);

      // If this is the first time we're seeing this AGV or the position changed, update our tracking
      if (lastPosition !== agv.current_node) {
        lastKnownPositions.current.set(agv.agv_id, agv.current_node);
      }
    });
  };

  // Initialize WebSocket connection
  const initWebSocket = () => {
    // Close any existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Create new WebSocket connection
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log("WebSocket connection established");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "agv_update") {
          // Update the AGV in the list data
          const updatedAgv = data.data;

          setListData((prevData) => {
            // If the AGV exists in the list, update it
            const agvIndex = prevData.findIndex(
              (agv) => agv.agv_id === updatedAgv.agv_id,
            );

            if (agvIndex !== -1) {
              const newData = [...prevData];
              newData[agvIndex] = updatedAgv;

              // Track position changes for animation
              const lastPosition = lastKnownPositions.current.get(
                updatedAgv.agv_id,
              );
              if (lastPosition !== updatedAgv.current_node) {
                lastKnownPositions.current.set(
                  updatedAgv.agv_id,
                  updatedAgv.current_node,
                );
              }

              return newData;
            }

            // If the AGV doesn't exist in the list, add it
            return [...prevData, updatedAgv];
          });
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      // Attempt to reconnect after a delay
      setTimeout(initWebSocket, 5000);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket connection closed: ${event.code}`);
      // Attempt to reconnect after a delay if the close was unexpected
      if (event.code !== 1000) {
        setTimeout(initWebSocket, 5000);
      }
    };

    // Store the WebSocket reference
    wsRef.current = ws;
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
      await fetchListData(); // This will update hasDispatchedOrders
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
      const cachedData = localStorage.getItem(CACHED_MAP_DATA_KEY);
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
      localStorage.setItem(CACHED_MAP_DATA_KEY, JSON.stringify(data));
    } catch (error) {
      console.error("Error fetching map data:", error);
      toast.error("Failed to load map data.");
    }
  };

  // Set up WebSocket connection and initial data loading
  useEffect(() => {
    // Fetch initial data
    fetchListData();

    // Initialize WebSocket connection
    initWebSocket();

    // Show map
    handleShowMap();

    // Clean up on component unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="space-y-5">
      <h2 className="text-3xl font-bold">AGVs</h2>

      <div className="flex flex-1 flex-col">
        <div className="gap-2">
          <div className="flex flex-col gap-4 md:gap-6">
            {/* Map Visualization Section */}
            <div>
              {mapData ? (
                <MapVisualizer data={mapData} agvs={listData} />
              ) : (
                <div className="rounded-md border border-dashed p-6 text-center">
                  <p className="text-muted-foreground">
                    No map data available. Please make sure you've imported CSV
                    data on the Map page.
                  </p>
                </div>
              )}
            </div>
            <Separator className="my-4" />
            <div className="grid grid-cols-4 gap-4">
              <div className="grid grid-rows-2 gap-4">
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
              <div className="col-end-4 grid grid-rows-2 gap-4">
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
            </div>
            <DataTable
              data={listData}
              columns={columns1(handleClickBtnDelete)}
              filterSearchByColumn="agv_id"
              onRowSelectionChange={setRowSelection}
              rowSelection={rowSelection}
            />
            <Separator className="my-4" />
            <DataTable
              data={listData}
              columns={columns2()}
              filterSearchByColumn="agv_id"
              onRowSelectionChange={setRowSelection}
              rowSelection={rowSelection}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
