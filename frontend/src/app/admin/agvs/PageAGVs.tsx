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
import { AGV } from "@/types/AGV.types";
import { CalendarPlus } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AlgorithmSelect } from "../schedules/AlgorithmSelect";
import { columnsTableAGVs } from "./columnsTableAGVs";
import { DialogFormCreateAGVs } from "./DialogFormCreateAGVs";
import { FormSimulateUpdateAgvPosition } from "./FormSimulateUpdateAgvPosition";

export function PageAGVs() {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [listData, setListData] = useState<AGV[]>([]);
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
      toast.success("Schedules generated successfully");
      await fetchListData();
    } catch (error) {
      if (error instanceof Response) {
        const errorData = await error.json();
        toast.error(errorData.error || "Failed to generate schedules");
      } else {
        toast.error("Failed to generate schedules");
      }
      console.error("Error generating schedules:", error);
    } finally {
      setIsDispatching(false);
    }
  };

  useEffect(() => {
    fetchListData();
  }, []);

  return (
    <div className="space-y-5">
      <h2 className="text-3xl font-bold">AGVs</h2>

      <div className="flex flex-1 flex-col">
        <div className="@container/main flex flex-1 flex-col gap-2">
          <div className="flex flex-col gap-4 md:gap-6">
            <div className="grid grid-cols-1 gap-10 xl:grid-cols-6">
              <div className="flex flex-col gap-4">
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
              <div className="flex flex-col gap-4">
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
              <div className="col-span-3">
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
          </div>
        </div>
      </div>
    </div>
  );
}
