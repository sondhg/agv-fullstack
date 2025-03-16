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
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
        <div className="flex items-center space-x-4">
          {/* Dropdown for selecting the algorithm */}
          {/* <select
            value={selectedAlgorithm}
            onChange={(e) => setSelectedAlgorithm(e.target.value)}
            className="rounded border px-3 py-2"
          >
            <option value="dijkstra">Dijkstra</option>
            <option value="q_learning">Q-Learning</option>
          </select> */}

          <Select
            onValueChange={(value) => setSelectedAlgorithm(value)} // Update the selected algorithm
            defaultValue="dijkstra" // Default value
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select Algorithm" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Algorithms</SelectLabel>
                <SelectItem value="dijkstra">Dijkstra</SelectItem>
                <SelectItem value="q_learning">Q-Learning</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

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
