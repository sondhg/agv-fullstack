import { useTableSelection } from "@/hooks/useTableSelection";
import { deleteOrder, getOrders } from "@/services/APIs/ordersAPI";
import { Order } from "@/types/Order.types";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { OrdersActionButtons } from "./OrdersActionButtons";
import { OrdersHeader } from "./OrdersHeader";
import { OrdersTable } from "./OrdersTable";

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

  useEffect(() => {
    fetchListData();
  }, []);

  return (
    <>
      <div className="space-y-5">
        <OrdersHeader />

        <OrdersActionButtons
          isCreateDialogOpen={isCreateDialogOpen}
          setIsCreateDialogOpen={setIsCreateDialogOpen}
          isUpdateDialogOpen={isUpdateDialogOpen}
          setIsUpdateDialogOpen={setIsUpdateDialogOpen}
          fetchListData={fetchListData}
          orderToUpdate={currentOrderToUpdate}
          selectedOrderIds={selectedOrderIds}
          resetSelection={resetSelection}
          listOrders={listOrders}
        />

        <OrdersTable
          listOrders={listOrders}
          handleClickBtnDelete={handleClickBtnDelete}
          handleClickBtnUpdate={handleClickBtnUpdate}
          rowSelection={rowSelection}
          setRowSelection={setRowSelection}
        />
      </div>
    </>
  );
}
