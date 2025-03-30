import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import {
  deleteOrder,
  getOrders,
  bulkDeleteOrders,
} from "@/services/APIs/ordersAPI";
import { handleExportCSV } from "@/services/CSV/csvExport";
import { useCSVImport } from "@/services/CSV/useCSVImport";
import { Order } from "@/types/Order.types";
import { FileDown, FileUp, Trash2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { columnsTableOrders } from "./columnsTableOrders";
import { DialogFormCreateOrders } from "./DialogFormCreateOrders";
import { DialogInstructionsCSV } from "./DialogInstructionsCSV";

export function PageOrders() {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [listData, setListData] = useState<Order[]>([]);

  const [rowSelection, setRowSelection] = useState<Record<string, boolean>>({});
  const [selectedOrderIds, setSelectedOrderIds] = useState<number[]>([]);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const { handleImportCSV } = useCSVImport();

  // Add this effect to convert row selection to IDs
  useEffect(() => {
    const selectedIds = Object.keys(rowSelection)
      .filter((key) => rowSelection[key])
      .map((rowIndex) => listData[parseInt(rowIndex)].order_id);

    setSelectedOrderIds(selectedIds);
  }, [rowSelection, listData]);

  const fetchListData = async () => {
    const data = await getOrders();
    setListData(data);
  };

  const handleClickBtnDelete = async (order_id: number) => {
    console.log(">>> delete order with id: ", order_id);

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

  // Add the mass delete handler (same as before)
  const handleMassDelete = async () => {
    if (selectedOrderIds.length === 0) {
      toast.error("Please select at least one order to delete");
      return;
    }

    try {
      await bulkDeleteOrders(selectedOrderIds);
      toast.success(`${selectedOrderIds.length} orders deleted successfully`);
      await fetchListData();
      setRowSelection({});
    } catch (error) {
      if (error instanceof Response) {
        const errorData = await error.json();
        toast.error(errorData.error || "Failed to delete orders");
      } else {
        toast.error("Failed to delete orders");
      }
      console.error("Mass delete error:", error);
    }
  };

  useEffect(() => {
    fetchListData();
  }, []);

  return (
    <>
      <div className="space-y-5">
        <h2 className="text-3xl font-bold">Orders</h2>
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
          <Button
            variant="destructive"
            onClick={handleMassDelete}
            disabled={selectedOrderIds.length === 0}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Mass Delete Orders
          </Button>
        </div>

        <DataTable
          data={listData}
          columns={columnsTableOrders(handleClickBtnDelete)}
          filterSearchByColumn="order_date"
          onRowSelectionChange={setRowSelection} // Add this
          rowSelection={rowSelection} // Add this
        />
      </div>
    </>
  );
}
