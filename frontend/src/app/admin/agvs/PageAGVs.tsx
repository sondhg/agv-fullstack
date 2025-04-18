import { DataTable } from "@/components/ui/data-table";
import { MassDeleteButton } from "@/components/ui/mass-delete-button";
import { useTableSelection } from "@/hooks/useTableSelection";
import { bulkDeleteAGVs, deleteAGV, getAGVs } from "@/services/APIs/agvsAPI";
import { AGV } from "@/types/AGV.types";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { DialogFormCreateAGVs } from "./DialogFormCreateAGVs";
import { columnsTableAGVs } from "./columnsTableAGVs";

export function PageAGVs() {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [listData, setListData] = useState<AGV[]>([]);
  const { rowSelection, setRowSelection, selectedIds: selectedAgvIds, resetSelection } = 
    useTableSelection<AGV>(listData, "agv_id");

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
        <MassDeleteButton
          selectedIds={selectedAgvIds}
          onDelete={bulkDeleteAGVs}
          itemName="AGVs"
          onSuccess={fetchListData}
          resetSelection={resetSelection}
        />
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
