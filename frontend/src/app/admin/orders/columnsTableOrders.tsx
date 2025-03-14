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
    accessorKey: "start_point",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Start Point" />
    ),
  },
  {
    accessorKey: "end_point",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="End Point" />
    ),
  },
  {
    accessorKey: "load_name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Load Name" />
    ),
  },
  {
    accessorKey: "load_amount",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Load Amount" />
    ),
    cell: ({ row }) => {
      const load_amount = row.getValue("load_amount");
      return <div>{`${load_amount} units`}</div>;
    },
  },
  {
    accessorKey: "load_weight",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Load Weight" />
    ),
    cell: ({ row }) => {
      const load_weight = row.getValue("load_weight");
      return <div>{`${load_weight} kg`}</div>;
    },
  },
  {
    accessorKey: "user_name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Username" />
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
