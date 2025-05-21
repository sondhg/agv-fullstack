import { DataTable } from "@/components/ui/data-table";
import { Order } from "@/types/Order.types";
import { OnChangeFn, RowSelectionState } from "@tanstack/react-table";
import { columnsTableOrders } from "./columnsTableOrders";

interface OrdersTableProps {
  listOrders: Order[];
  handleClickBtnDelete: (order_id: number) => Promise<void>;
  handleClickBtnUpdate: (order: Order) => void;
  rowSelection: RowSelectionState;
  setRowSelection: OnChangeFn<RowSelectionState>;
}

export function OrdersTable({
  listOrders,
  handleClickBtnDelete,
  handleClickBtnUpdate,
  rowSelection,
  setRowSelection,
}: OrdersTableProps) {
  return (
    <DataTable
      data={listOrders}
      columns={columnsTableOrders(handleClickBtnDelete, handleClickBtnUpdate)}
      filterSearchByColumn="order_date"
      onRowSelectionChange={setRowSelection}
      rowSelection={rowSelection}
    />
  );
}
