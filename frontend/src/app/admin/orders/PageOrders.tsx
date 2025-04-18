import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { MassDeleteButton } from "@/components/ui/mass-delete-button";
import { useTableSelection } from "@/hooks/useTableSelection";
import {
  deleteOrder,
  getOrders,
  bulkDeleteOrders,
} from "@/services/APIs/ordersAPI";
import { handleExportCSV } from "@/services/CSV/csvExport";
import { useCSVImport } from "@/services/CSV/useCSVImport";
import { Order } from "@/types/Order.types";
import { FileDown, FileUp } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { columnsTableOrders } from "./columnsTableOrders";
import { DialogFormCreateOrders } from "./DialogFormCreateOrders";
import { DialogInstructionsCSV } from "./DialogInstructionsCSV";
import { AlertTravelRoute } from "./AlertTravelRoute";

export function PageOrders() {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [listData, setListData] = useState<Order[]>([]);
  const {
    rowSelection,
    setRowSelection,
    selectedIds: selectedOrderIds,
    resetSelection,
  } = useTableSelection<Order>(listData, "order_id");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { handleImportCSV } = useCSVImport();

  const fetchListData = async () => {
    const data = await getOrders();
    setListData(data);
  };

  const handleClickBtnDelete = async (order_id: number) => {
    try {
      await deleteOrder(order_id);
      toast.success("Delete order successfully");
      await fetchListData();
    } catch (error) {
      console.error("Failed to delete order:", error);
      toast.error("Failed to delete order. Please try again.");
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleImportCSV(file, fetchListData).finally(() => {
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      });
    }
  };

  useEffect(() => {
    fetchListData();
  }, []);

  return (
    <>
      <div className="space-y-5">
        <h2 className="text-3xl font-bold">Orders</h2>
        <AlertTravelRoute />
        <div className="space-x-5">
          <DialogFormCreateOrders
            isDialogOpen={isDialogOpen}
            setIsDialogOpen={setIsDialogOpen}
            fetchListData={fetchListData}
          />
          <Button onClick={() => fileInputRef.current?.click()}>
            <FileUp />
            Import CSV
          </Button>
          <input
            type="file"
            ref={fileInputRef}
            accept=".csv"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button
            variant={"secondary"}
            onClick={() => handleExportCSV(listData)}
          >
            <FileDown />
            Export CSV
          </Button>
          <DialogInstructionsCSV />
          <MassDeleteButton
            selectedIds={selectedOrderIds}
            onDelete={bulkDeleteOrders}
            itemName="Orders"
            onSuccess={fetchListData}
            resetSelection={resetSelection}
          />
        </div>

        <DataTable
          data={listData}
          columns={columnsTableOrders(handleClickBtnDelete)}
          filterSearchByColumn="order_date"
          onRowSelectionChange={setRowSelection}
          rowSelection={rowSelection}
        />
      </div>
    </>
  );
}
