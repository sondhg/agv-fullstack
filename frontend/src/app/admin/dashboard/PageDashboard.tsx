import { Button } from "@/components/ui/button"; // Import a button component for toggling pause
import { DataTable } from "@/components/ui/data-table";
import { WebSocketData } from "@/types/WebSocket.types";
import { Pause, Play } from "lucide-react";
import { useEffect, useState } from "react";
import { columnsTableDashboard } from "./columnsTableDashboard";
import { SpeedLineChart } from "./SpeedLineChart";

export function PageDashboard() {
  const [agvDataMap, setAgvDataMap] = useState<Record<number, WebSocketData>>(
    {},
  );
  const [paused, setPaused] = useState(false); // New paused state

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/data/");

    ws.onmessage = (event) => {
      if (paused) return; // Skip updates if paused

      const data = JSON.parse(event.data);

      if (data.agvs_array_data) {
        setAgvDataMap((prevData) => {
          const updatedData = { ...prevData };
          data.agvs_array_data.forEach((agv: WebSocketData) => {
            updatedData[agv.car_id] = agv; // Update or add AGV data based on car_id
          });
          return updatedData;
        });
      }
    };

    return () => {
      ws.close();
    };
  }, [paused]); // Re-run effect if paused changes

  const agvDataArray = Object.values(agvDataMap);

  return (
    <div>
      <div className="space-y-5">
        <h2 className="text-3xl font-bold">Dashboard</h2>
        <Button variant="outline" onClick={() => setPaused((prev) => !prev)}>
          {paused ? (
            <>
              <Play />
              Resume Updates
            </>
          ) : (
            <>
              <Pause />
              Pause Updates
            </>
          )}
        </Button>
        <SpeedLineChart agvDataArray={agvDataArray} />
        <DataTable
          data={agvDataArray}
          columns={columnsTableDashboard}
          filterSearchByColumn="car_id"
        />
      </div>
    </div>
  );
}
