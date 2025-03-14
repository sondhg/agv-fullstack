import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import {
  createSchedule,
  getSchedules,
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
    console.log(">>> data: ", data);
    setListData(data);
  };

  const handleCreateSchedule = async () => {
    try {
      setIsCreating(true);
      await createSchedule();
      toast.success("Schedule created successfully");
      await fetchListData(); // Refresh the list after creating
    } catch (error) {
      toast.error("Failed to create schedule");
      console.error("Error creating schedule:", error);
    } finally {
      setIsCreating(false);
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
            {isCreating ? "Creating Schedule..." : "Create Schedule"}
          </Button>
        </div>
        <DataTable
          data={listData}
          columns={columnsTableSchedules}
          filterSearchByColumn="order_date"
        />
      </div>
    </div>
  );
}
