import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MassDeleteButton } from "@/components/ui/mass-delete-button";
import { useTableSelection } from "@/hooks/useTableSelection";
import {
  bulkDeleteOrders,
  createMultipleOrdersBatch,
  deleteOrder,
  getOrders,
} from "@/services/APIs/ordersAPI";
import { handleExportCSV } from "@/services/CSV/csvExport";
import { useCSVImport } from "@/services/CSV/useCSVImport";
import { CreateOrderDto, Order } from "@/types/Order.types";
import { FileDown, FileUp, ListPlus } from "lucide-react";
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

  // Function to get the current date in the format YYYY-MM-DD
  const getCurrentDate = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  // Function to calculate the start time at least minutesFromNow minutes from current time
  const getStartTime = (minutesFromNow: number) => {
    const baseTime = new Date();
    baseTime.setSeconds(0);
    baseTime.setMinutes(baseTime.getMinutes() + 1);
    baseTime.setMinutes(baseTime.getMinutes() + (minutesFromNow - 1));

    const hours = String(baseTime.getHours()).padStart(2, "0");
    const minutes = String(baseTime.getMinutes()).padStart(2, "0");

    return `${hours}:${minutes}:00`;
  };

  // Generate example orders data
  const generateExampleOrders = (
    example: "example1and2" | "example3",
  ): CreateOrderDto[] => {
    const currentDate = getCurrentDate();

    if (example === "example1and2") {
      return [
        {
          order_id: 1,
          order_date: currentDate,
          start_time: getStartTime(1),
          parking_node: 7,
          storage_node: 15,
          workstation_node: 23,
        },
        {
          order_id: 2,
          order_date: currentDate,
          start_time: getStartTime(2),
          parking_node: 19,
          storage_node: 11,
          workstation_node: 16,
        },
        {
          order_id: 3,
          order_date: currentDate,
          start_time: getStartTime(3),
          parking_node: 13,
          storage_node: 11,
          workstation_node: 9,
        },
      ];
    } else {
      return [
        {
          order_id: 1,
          order_date: currentDate,
          start_time: getStartTime(1),
          parking_node: 7,
          storage_node: 5,
          workstation_node: 21,
        },
        {
          order_id: 2,
          order_date: currentDate,
          start_time: getStartTime(2),
          parking_node: 17,
          storage_node: 10,
          workstation_node: 22,
        },
        {
          order_id: 3,
          order_date: currentDate,
          start_time: getStartTime(3),
          parking_node: 32,
          storage_node: 15,
          workstation_node: 19,
        },
      ];
    }
  };

  // Handle creating example orders directly
  const handleCreateExampleOrders = async (
    example: "example1and2" | "example3",
  ) => {
    try {
      const orders = generateExampleOrders(example);
      await createMultipleOrdersBatch(orders);
      toast.success(`Created ${orders.length} example orders successfully`);
      await fetchListData();
    } catch (error) {
      console.error("Failed to create example orders:", error);
      toast.error("Failed to create example orders. Please try again.");
    }
  };

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
          </Button>{" "}
          <DialogInstructionsCSV />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <ListPlus className="mr-2 h-4 w-4" />
                Create Example Orders
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem
                onClick={() => handleCreateExampleOrders("example1and2")}
              >
                Example 1 and 2
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => handleCreateExampleOrders("example3")}
              >
                Example 3
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
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
