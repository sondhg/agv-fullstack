"use client";

import { ColumnDef } from "@tanstack/react-table";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { Order } from "@/types/Order.types";
import { createBaseColumns } from "@/components/ui/base-table-columns";

export const columnsTableOrders = (
  handleClickBtnDelete: (orderId: number) => void,
): ColumnDef<Order>[] => {
  const baseColumns = createBaseColumns<Order>(handleClickBtnDelete, "order_id");
  const [selectColumn, actionsColumn] = baseColumns;
  
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
    actionsColumn,
  ];
};
