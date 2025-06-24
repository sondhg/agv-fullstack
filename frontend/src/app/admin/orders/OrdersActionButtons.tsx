import { MassDeleteButton } from "@/components/ui/mass-delete-button";
import { bulkDeleteOrders } from "@/services/APIs/ordersAPI";
import { Order } from "@/types/Order.types";
import { Dispatch, SetStateAction } from "react";
import { DialogFormCreateOrders } from "./DialogFormCreateOrders";
import { DialogFormUpdateOrders } from "./DialogFormUpdateOrders";
import { OrdersCSVActions } from "./OrdersCSVActions";
import { OrdersExampleGenerator } from "./OrdersExampleGenerator";

interface OrdersActionButtonsProps {
  isCreateDialogOpen: boolean;
  setIsCreateDialogOpen: Dispatch<SetStateAction<boolean>>;
  isUpdateDialogOpen: boolean;
  setIsUpdateDialogOpen: Dispatch<SetStateAction<boolean>>;
  fetchListData: () => Promise<void>;
  orderToUpdate: Order | null;
  selectedOrderIds: number[];
  resetSelection: () => void;
  listOrders: Order[];
}

export function OrdersActionButtons({
  isCreateDialogOpen,
  setIsCreateDialogOpen,
  isUpdateDialogOpen,
  setIsUpdateDialogOpen,
  fetchListData,
  orderToUpdate,
  selectedOrderIds,
  resetSelection,
  listOrders,
}: OrdersActionButtonsProps) {
  return (
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
        orderToUpdate={orderToUpdate}
      />
      <OrdersCSVActions listOrders={listOrders} fetchListData={fetchListData} />
      {/* Hide for final screenshots */}
      {/* <OrdersExampleGenerator fetchListData={fetchListData} /> */}
      <MassDeleteButton
        selectedIds={selectedOrderIds}
        onDelete={bulkDeleteOrders}
        itemName="Orders"
        onSuccess={fetchListData}
        resetSelection={resetSelection}
      />
    </div>
  );
}
