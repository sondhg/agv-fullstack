import { DataTable } from "@/components/ui/data-table";
import { deleteAGV, getAGVs } from "@/services/APIs/agvAPI";
import { AGV } from "@/types/AGV.types";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { columnsTableAGVs } from "./columnsTableAGVs";
import { DialogFormCreateAGVs } from "./DialogFormCreateAGVs";

export function PageAGVs() {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [listData, setListData] = useState<AGV[]>([]);

  const fetchListData = async () => {
    const data = await getAGVs();
    console.log(">>> data: ", data);
    setListData(data);
  };

  const handleClickBtnDelete = async (order_id: number) => {
    console.log(">>> delete order with id: ", order_id);

    try {
      await deleteAGV(order_id);
      toast.success("Delete order successfully");
      await fetchListData();
    } catch (error) {
      console.error("Failed to delete order:", error);
      toast.error("Failed to delete order. Please try again.");
    }
  };

  useEffect(() => {
    fetchListData();
  }, []);

  return (
    <div>
      <div className="space-y-5">
        <h2 className="text-3xl font-bold">AGVs</h2>
        <DialogFormCreateAGVs
          isDialogOpen={isDialogOpen}
          setIsDialogOpen={setIsDialogOpen}
          fetchListData={fetchListData}
        />
        <DataTable
          data={listData}
          columns={columnsTableAGVs(handleClickBtnDelete)}
          filterSearchByColumn="agv_id"
        />
      </div>
    </div>
  );
}
