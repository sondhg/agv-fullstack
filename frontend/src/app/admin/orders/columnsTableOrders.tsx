"use client";

import { ColumnDef } from "@tanstack/react-table";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { Order } from "@/types/Order.types";
import { Trash2 } from "lucide-react";

export const columnsTableOrders = (
  handleClickBtnDelete: (orderId: number) => void,
): ColumnDef<Order>[] => [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
  },
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
  {
    id: "actions",
    cell: ({ row }) => {
      const order = row.original;

      return (
        <Button
          variant={"destructive"}
          onClick={() => handleClickBtnDelete(order.order_id)}
        >
          <Trash2 />
        </Button>
      );
    },
  },
];
