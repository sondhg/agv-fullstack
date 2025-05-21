import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { MassDeleteButton } from "@/components/ui/mass-delete-button";
import { useTableSelection } from "@/hooks/useTableSelection";
import {
  bulkDeleteOrders,
  deleteOrder,
  getOrders,
} from "@/services/APIs/ordersAPI";
import { handleExportCSV } from "@/services/CSV/csvExport";
import { useCSVImport } from "@/services/CSV/useCSVImport";
import { Order } from "@/types/Order.types";
import { FileDown, FileUp } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { AlertTravelRoute } from "./AlertTravelRoute";
import { columnsTableOrders } from "./columnsTableOrders";
import { DialogFormCreateOrders } from "./DialogFormCreateOrders";
import { DialogFormUpdateOrders } from "./DialogFormUpdateOrders";
import { DialogInstructionsCSV } from "./DialogInstructionsCSV";

export function PageOrders() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState<boolean>(false);
  const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState<boolean>(false);
  const [currentOrderToUpdate, setCurrentOrderToUpdate] =
    useState<Order | null>(null);
  const [listOrders, setListOrders] = useState<Order[]>([]);
  const {
    rowSelection,
    setRowSelection,
    selectedIds: selectedOrderIds,
    resetSelection,
  } = useTableSelection<Order>(listOrders, "order_id");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { handleImportCSV } = useCSVImport();

  const fetchListData = async () => {
    const data = await getOrders();
    setListOrders(data);
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

  const handleClickBtnUpdate = (order: Order) => {
    setCurrentOrderToUpdate(order);
    setIsUpdateDialogOpen(true);
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
            isDialogOpen={isCreateDialogOpen}
            setIsDialogOpen={setIsCreateDialogOpen}
            fetchListData={fetchListData}
          />
          <DialogFormUpdateOrders
            isDialogOpen={isUpdateDialogOpen}
            setIsDialogOpen={setIsUpdateDialogOpen}
            fetchListData={fetchListData}
            orderToUpdate={currentOrderToUpdate}
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
            onClick={() => handleExportCSV(listOrders)}
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
          data={listOrders}
          columns={columnsTableOrders(
            handleClickBtnDelete,
            handleClickBtnUpdate,
          )}
          filterSearchByColumn="order_date"
          onRowSelectionChange={setRowSelection}
          rowSelection={rowSelection}
        />
      </div>
    </>
  );
}
