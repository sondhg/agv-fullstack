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
  resetAGVs,
  scheduleHelloMessage,
} from "@/services/APIs/agvsAPI";
import { fetchMapData } from "@/services/APIs/mapAPI";
import { AGV } from "@/types/AGV.types";
import { MapData } from "@/types/Map.types";
import { Order } from "@/types/Order.types";
import { Bell, CalendarPlus, RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { MapVisualizer } from "../map/MapVisualizer";
import { AlgorithmSelect } from "./AlgorithmSelect";
import { columns1 } from "./columns1";
import { columns2 } from "./columns2";
import { DialogFormCreateAGVs } from "./DialogFormCreateAGVs";
import { DialogViewOrderInfo } from "./DialogViewOrderInfo";

export function PageAGVs() {
  // Core state
  const [agvs, setAgvs] = useState<AGV[]>([]);
  const [mapData, setMapData] = useState<MapData | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isOrderDialogOpen, setIsOrderDialogOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isDispatching, setIsDispatching] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [isSchedulingHello, setIsSchedulingHello] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState("dijkstra");
  // Table selection state
  const {
    rowSelection,
    setRowSelection,
    selectedIds: selectedAgvIds,
    resetSelection,
  } = useTableSelection<AGV>(agvs, "agv_id");

  // Check if any AGV has orders dispatched to them
  const hasAGVsWithOrders = agvs.some((agv) => agv.active_order_info !== null);

  // Load initial data
  useEffect(() => {
    // Load AGV data
    const loadAgvData = async () => {
      try {
        const data = await getAGVs();
        setAgvs(data);
      } catch (error) {
        console.error("Failed to load AGV data:", error);
        toast.error("Failed to load AGV data");
      }
    };

    // Load map data
    const loadMapData = async () => {
      try {
        // Try to get from localStorage first
        const cachedData = localStorage.getItem(CACHED_MAP_DATA_KEY);
        if (cachedData) {
          setMapData(JSON.parse(cachedData) as MapData);
          return;
        }

        // Fetch from backend if not cached
        const data = (await fetchMapData()) as MapData;
        if (!data || !data.nodes || !data.connections || !data.directions) {
          toast.error("Failed to load map data");
          return;
        }

        setMapData(data);
        localStorage.setItem(CACHED_MAP_DATA_KEY, JSON.stringify(data));
      } catch (error) {
        console.error("Failed to load map data:", error);
        toast.error("Failed to load map data");
      }
    };

    // Setup WebSocket
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => console.log("WebSocket connection established");

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "agv_update") {
          const updatedAgv = data.data;

          setAgvs((prevAgvs) => {
            const index = prevAgvs.findIndex(
              (agv) => agv.agv_id === updatedAgv.agv_id,
            );

            if (index !== -1) {
              // Update existing AGV
              const newAgvs = [...prevAgvs];
              newAgvs[index] = updatedAgv;
              return newAgvs;
            } else {
              // Add new AGV
              return [...prevAgvs, updatedAgv];
            }
          });
        }
      } catch (error) {
        console.error("Error handling WebSocket message:", error);
      }
    };

    ws.onerror = () => console.error("WebSocket error occurred");

    // Load data
    loadAgvData();
    loadMapData();

    // Cleanup on unmount
    return () => ws.close();
  }, []);

  // Handler functions
  const refreshAgvData = async () => {
    try {
      const data = await getAGVs();
      setAgvs(data);
    } catch (error) {
      console.error("Failed to refresh AGV data:", error);
      toast.error("Failed to refresh AGV data");
    }
  };
  const handleDeleteAgv = async (agv_id: number) => {
    try {
      await deleteAGV(agv_id);
      toast.success("AGV deleted successfully");
      await refreshAgvData();
    } catch (error) {
      console.error("Failed to delete AGV:", error);
      toast.error("Failed to delete AGV");
    }
  };

  const handleClickActiveOrder = (order: Order) => {
    setSelectedOrder(order);
    setIsOrderDialogOpen(true);
  };  const handleDispatchOrders = async () => {
    try {
      setIsDispatching(true);
      const response = await dispatchOrdersToAGVs(selectedAlgorithm);
      
      // Handle the new scheduling response structure
      if (response && typeof response === 'object') {
        const scheduledCount = response.scheduled_orders?.length || 0;
        const immediateCount = response.immediate_orders?.length || 0;
        const totalCount = response.total_processed || 0;
        
        if (totalCount > 0) {
          let message = "Orders processed successfully! ";
          if (scheduledCount > 0 && immediateCount > 0) {
            message += `Scheduled ${scheduledCount} orders for future execution and assigned ${immediateCount} orders immediately.`;
          } else if (scheduledCount > 0) {
            message += `Scheduled ${scheduledCount} orders for future execution.`;
          } else if (immediateCount > 0) {
            message += `Assigned ${immediateCount} orders immediately.`;
          }
          toast.success(message);
        } else {
          toast.info("No orders were processed. Check that you have available orders and idle AGVs.");
        }
      } else {
        toast.success("Orders scheduled successfully");
      }
      
      await refreshAgvData();
    } catch (error) {
      let errorMessage = "Failed to schedule orders";

      if (error instanceof Response) {
        try {
          const errorData = await error.json();
          errorMessage = errorData.message || errorData.error || errorMessage;
        } catch {
          // If error parsing fails, use default message
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }

      toast.error(errorMessage);
      console.error("Error scheduling orders:", error);
    } finally {
      setIsDispatching(false);
    }
  };
  const handleResetAGVs = async () => {
    try {
      setIsResetting(true);
      const response = await resetAGVs();
      toast.success(response.message);
      await refreshAgvData();
    } catch (error) {
      toast.error("Failed to reset AGVs");
      console.error("Error resetting AGVs:", error);
    } finally {
      setIsResetting(false);
    }
  };

  const handleScheduleHelloMessage = async () => {
    try {
      setIsSchedulingHello(true);
      const response = await scheduleHelloMessage();
      console.log(">>> response:", response);
      toast.success("Hello messages scheduled successfully");
      await refreshAgvData();
    } catch (error) {
      toast.error("Failed to schedule hello messages");
      console.error("Error scheduling hello messages:", error);
    } finally {
      setIsSchedulingHello(false);
    }
  };

  return (
    <div className="space-y-5">
      <h2 className="text-3xl font-bold">AGVs</h2>

      <div className="flex flex-1 flex-col">
        <div className="gap-2">
          <div className="flex flex-col gap-4 md:gap-6">
            {/* Map Visualization Section */}
            <div>
              {mapData ? (
                <MapVisualizer data={mapData} agvs={agvs} />
              ) : (
                <div className="rounded-md border border-dashed p-6 text-center">
                  <p className="text-muted-foreground">
                    No map data available. Please make sure you've imported CSV
                    data on the Map page.
                  </p>
                </div>
              )}
            </div>{" "}
            <Separator className="my-4" />
            <div className="flex w-full items-start justify-between">
              <div className="grid w-[28%] grid-rows-2 gap-4">
                <DialogFormCreateAGVs
                  isDialogOpen={isDialogOpen}
                  setIsDialogOpen={setIsDialogOpen}
                  fetchListData={refreshAgvData}
                />
                <MassDeleteButton
                  selectedIds={selectedAgvIds}
                  onDelete={bulkDeleteAGVs}
                  itemName="AGVs"
                  onSuccess={refreshAgvData}
                  resetSelection={resetSelection}
                />
              </div>
              <div className="grid w-[28%] grid-rows-2 gap-4">                <Button
                  onClick={handleDispatchOrders}
                  disabled={isDispatching}
                  className="w-full"
                >
                  <CalendarPlus className="mr-2 h-4 w-4" />
                  {isDispatching
                    ? "Scheduling..."
                    : "Schedule orders to AGVs"}{" "}
                </Button>
                <AlgorithmSelect
                  selectedAlgorithm={selectedAlgorithm}
                  onAlgorithmChange={(value) => setSelectedAlgorithm(value)}
                />
              </div>{" "}
              <div className="grid w-[28%] grid-rows-2 gap-4">
                <Button
                  onClick={handleScheduleHelloMessage}
                  disabled={isSchedulingHello || !hasAGVsWithOrders}
                  variant="default"
                  className="w-full"
                >
                  <Bell className="mr-2 h-4 w-4" />
                  {isSchedulingHello
                    ? "Scheduling..."
                    : "Schedule Hello Messages"}
                </Button>
                <Button
                  onClick={handleResetAGVs}
                  disabled={isResetting}
                  variant="destructive"
                  className="w-full"
                >
                  <RefreshCcw className="mr-2 h-4 w-4" />
                  {isResetting ? "Resetting..." : "Reset AGVs"}
                </Button>
              </div>
            </div>{" "}
            <DataTable
              data={agvs}
              columns={columns1(handleDeleteAgv, handleClickActiveOrder)}
              filterSearchByColumn="agv_id"
              onRowSelectionChange={setRowSelection}
              rowSelection={rowSelection}
            />
            <Separator className="my-4" />
            <DataTable
              data={agvs}
              columns={columns2()}
              filterSearchByColumn="agv_id"
              onRowSelectionChange={setRowSelection}
              rowSelection={rowSelection}
            />{" "}
          </div>
        </div>
      </div>

      <DialogViewOrderInfo
        isDialogOpen={isOrderDialogOpen}
        setIsDialogOpen={setIsOrderDialogOpen}
        orderToView={selectedOrder}
      />
    </div>
  );
}
