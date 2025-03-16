import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import {
  generateSchedules,
  getSchedules,
  deleteSchedule,
} from "@/services/APIs/schedulesAPI";
import { Schedule } from "@/types/Schedule.types";
import { CalendarPlus } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { columnsTableSchedules } from "./columnsTableSchedules";

export function PageSchedules() {
  const [listData, setListData] = useState<Schedule[]>([]);
  const [isCreating, setIsCreating] = useState(false);

  const fetchListData = async () => {
    const data = await getSchedules();
    setListData(data);
  };

  const handleCreateSchedule = async () => {
    try {
      setIsCreating(true);
      await generateSchedules();
      toast.success("Schedules generated successfully");
      await fetchListData(); // Refresh the list after generating
    } catch (error: any) {
      if (error.message) {
        toast.error(error.message); // Display the warning message
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
      console.error("Failed to delete schedule:", error);
      toast.error("Failed to delete schedule. Please try again.");
    }
  };

  useEffect(() => {
    fetchListData();
  }, []);

  return (
    <div>
      <div className="space-y-5">
        <h2 className="text-3xl font-bold">Schedules</h2>
        <div className="space-x-4">
          <Button onClick={fetchListData}>Fetch Schedules</Button>
          <Button
            onClick={handleCreateSchedule}
            disabled={isCreating}
            variant="secondary"
          >
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
