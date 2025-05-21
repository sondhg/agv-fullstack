"use client";

import { ColumnDef } from "@tanstack/react-table";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { Order } from "@/types/Order.types";
import { createBaseColumns } from "@/components/ui/base-table-columns";
import { Button } from "@/components/ui/button";
import { Pencil, Trash2 } from "lucide-react";

export const columnsTableOrders = (
  handleClickBtnDelete: (orderId: number) => void,
  handleClickBtnUpdate: (order: Order) => void,
): ColumnDef<Order>[] => {
  const baseColumns = createBaseColumns<Order>(
    handleClickBtnDelete,
    "order_id",
  );
  const [selectColumn] = baseColumns;
  // Create a custom actions column that includes both update and delete buttons
  const customActionsColumn: ColumnDef<Order> = {
    id: "actions",
    cell: ({ row }) => {
      const order = row.original;

      return (
        <div className="flex items-center justify-end gap-2">
          <Button size="icon" onClick={() => handleClickBtnUpdate(order)}>
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="destructive"
            size="icon"
            onClick={() => handleClickBtnDelete(order.order_id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      );
    },
  };

  return [
    selectColumn,
    {
      accessorKey: "order_id",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Order ID" />
      ),
      cell: ({ row }) => {
        const order_id = parseFloat(row.getValue("order_id"));
        return <div className="font-medium">{order_id}</div>;
      },
    },
    {
      accessorKey: "order_date",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Order Date" />
      ),
    },
    {
      accessorKey: "start_time",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Start Time" />
      ),
    },
    {
      accessorKey: "parking_node",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Parking Node" />
      ),
    },
    {
      accessorKey: "storage_node",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Storage Node" />
      ),
    },
    {
      accessorKey: "workstation_node",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Workstation Node" />
      ),
    },
    customActionsColumn,
  ];
};
