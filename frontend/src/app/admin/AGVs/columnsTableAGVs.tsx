"use client";

import { ColumnDef } from "@tanstack/react-table";

import { Checkbox } from "@/components/ui/checkbox";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { AGV } from "@/types/AGV.types";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

export const columnsTableAGVs = (
  handleClickBtnDelete: (agv_id: number) => void,
): ColumnDef<AGV>[] => [
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
    accessorKey: "agv_id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="AGV ID" />
    ),
  },
  {
    accessorKey: "max_speed",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Max Speed" />
    ),
  },
  {
    accessorKey: "max_battery",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Max Battery" />
    ),
  },
  {
    accessorKey: "max_load",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Max Load" />
    ),
  },
  {
    accessorKey: "guidance_type",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Guidance Type" />
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const agv = row.original;

      return (
        <Button
          variant={"destructive"}
          onClick={() => handleClickBtnDelete(agv.agv_id)}
        >
          <Trash2 />
        </Button>
      );
    },
  },
];
