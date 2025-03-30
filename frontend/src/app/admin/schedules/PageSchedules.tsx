import { AlgorithmSelect } from "@/app/admin/schedules/AlgorithmSelect";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import {
  deleteSchedule,
  generateSchedules,
  getSchedules,
} from "@/services/APIs/schedulesAPI";
import { Schedule } from "@/types/Schedule.types";
import { CalendarPlus, Terminal } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { columnsTableSchedules } from "./columnsTableSchedules";
import { AlertSchedulesGuide } from "./AlertSchedulesGuide";

export function PageSchedules() {
  const [listData, setListData] = useState<Schedule[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] =
    useState<string>("dijkstra"); // Default algorithm

  const fetchListData = async () => {
    const data = await getSchedules();
    setListData(data);
  };

  const handleCreateSchedule = async () => {
    try {
      setIsCreating(true);
      await generateSchedules(selectedAlgorithm); // Pass the selected algorithm
      toast.success("Schedules generated successfully");
      await fetchListData(); // Refresh the list after generating
    } catch (error) {
      if (error instanceof Response) {
        const errorData = await error.json();
        toast.error(errorData.error || "Failed to generate schedules");
      } else {
        toast.error("Failed to generate schedules");
      }
      console.error("Error generating schedules:", error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleClickBtnDelete = async (schedule_id: number) => {
    try {
      await deleteSchedule(schedule_id);
      toast.success("Schedule deleted successfully");
      await fetchListData(); // Refresh the list after deletion
    } catch (error) {
      if (error instanceof Response) {
        const errorData = await error.json();
        toast.error(errorData.error || "Failed to delete schedule");
      } else {
        toast.error("Failed to delete schedule. Please try again.");
      }
      console.error("Failed to delete schedule:", error);
    }
  };

  useEffect(() => {
    fetchListData();
  }, []);

  return (
    <div>
      <div className="space-y-5">
        <h2 className="text-3xl font-bold">Schedules</h2>
        <AlertSchedulesGuide />
        <div className="flex items-center space-x-4">
          {/* Use the AlgorithmSelect component */}
          <AlgorithmSelect
            selectedAlgorithm={selectedAlgorithm}
            onAlgorithmChange={(value) => setSelectedAlgorithm(value)}
          />

          <Button onClick={handleCreateSchedule} disabled={isCreating}>
            <CalendarPlus className="mr-2 h-4 w-4" />
            {isCreating ? "Generating Schedules..." : "Create Schedules"}
          </Button>
        </div>
        <DataTable
          data={listData}
          columns={columnsTableSchedules(handleClickBtnDelete)}
          filterSearchByColumn="order_date"
        />
      </div>
    </div>
  );
}
