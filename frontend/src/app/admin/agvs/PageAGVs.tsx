import { DataTable } from "@/components/ui/data-table";
import { bulkDeleteAGVs, deleteAGV, getAGVs } from "@/services/APIs/agvsAPI";
import { AGV } from "@/types/AGV.types";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { DialogFormCreateAGVs } from "./DialogFormCreateAGVs";
import { columnsTableAGVs } from "./columnsTableAGVs";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

export function PageAGVs() {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [listData, setListData] = useState<AGV[]>([]);
  const [rowSelection, setRowSelection] = useState<Record<string, boolean>>({});
  const [selectedAgvIds, setSelectedAgvIds] = useState<number[]>([]);

  // Add effect to convert row selection to IDs
  useEffect(() => {
    const selectedIds = Object.keys(rowSelection)
      .filter((key) => rowSelection[key])
      .map((rowIndex) => listData[parseInt(rowIndex)].agv_id);

    setSelectedAgvIds(selectedIds);
  }, [rowSelection, listData]);

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

  const handleMassDelete = async () => {
    if (selectedAgvIds.length === 0) {
      toast.error("Please select at least one AGV to delete");
      return;
    }

    try {
      await bulkDeleteAGVs(selectedAgvIds);
      toast.success(`${selectedAgvIds.length} AGVs deleted successfully`);
      await fetchListData();
      setRowSelection({});
    } catch (error) {
      if (error instanceof Response) {
        const errorData = await error.json();
        toast.error(errorData.error || "Failed to delete AGVs");
      } else {
        toast.error("Failed to delete AGVs");
      }
      console.error("Mass delete error:", error);
    }
  };

  useEffect(() => {
    fetchListData();
  }, []);

  return (
    <div className="space-y-5">
      <h2 className="text-3xl font-bold">AGVs</h2>
      <div className="space-x-5">
        <DialogFormCreateAGVs
          isDialogOpen={isDialogOpen}
          setIsDialogOpen={setIsDialogOpen}
          fetchListData={fetchListData}
        />
        <Button
          variant="destructive"
          onClick={handleMassDelete}
          disabled={selectedAgvIds.length === 0}
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Mass Delete AGVs
        </Button>
      </div>
      <DataTable
        data={listData}
        columns={columnsTableAGVs(handleClickBtnDelete)}
        filterSearchByColumn="agv_id"
        onRowSelectionChange={setRowSelection}
        rowSelection={rowSelection}
      />
    </div>
  );
}
