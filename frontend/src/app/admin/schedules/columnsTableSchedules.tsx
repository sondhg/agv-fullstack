"use client";

import { ColumnDef } from "@tanstack/react-table";

import { Checkbox } from "@/components/ui/checkbox";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { Schedule } from "@/types/Schedule.types";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

export const columnsTableSchedules = (
  handleClickBtnDelete: (scheduleId: number) => void,
): ColumnDef<Schedule>[] => [
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
    accessorKey: "schedule_id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Schedule ID" />
    ),
    cell: ({ row }) => {
      const schedule_id = parseFloat(row.getValue("schedule_id"));
      return <div className="font-medium">{schedule_id}</div>;
    },
  },
  {
    accessorKey: "order_id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Order ID" />
    ),
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
    accessorKey: "est_end_time",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Estimated End Time" />
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
  // {
  //   accessorKey: "load_name",
  //   header: ({ column }) => (
  //     <DataTableColumnHeader column={column} title="Load Name" />
  //   ),
  // },
  // {
  //   accessorKey: "load_amount",
  //   header: ({ column }) => (
  //     <DataTableColumnHeader column={column} title="Load Amount" />
  //   ),
  // },
  // {
  //   accessorKey: "load_weight",
  //   header: ({ column }) => (
  //     <DataTableColumnHeader column={column} title="Load Weight" />
  //   ),
  // },
  {
    accessorKey: "instruction_set",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Instruction Set" />
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const schedule = row.original;

      return (
        <Button
          variant={"destructive"}
          onClick={() => handleClickBtnDelete(schedule.schedule_id)}
        >
          <Trash2 />
        </Button>
      );
    },
  },
];
