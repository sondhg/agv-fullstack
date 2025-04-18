"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { AGV } from "@/types/AGV.types";
import { Trash2 } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";

export const columnsTableAGVs = (
  handleClickBtnDelete: (agvId: number) => void,
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
    cell: ({ row }) => {
      const agv_id = parseFloat(row.getValue("agv_id"));
      return <div className="font-medium">{agv_id}</div>;
    },
  },
  {
    accessorKey: "preferred_parking_node",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Preferred Parking Node" />
    ),
  },
  {
    accessorKey: "current_node",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Current Node" />
    ),
  },
  {
    accessorKey: "next_node",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Next Node" />
    ),
  },
  {
    accessorKey: "reserved_node",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Reserved Node" />
    ),
  },
  {
    accessorKey: "motion_state",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Motion State" />
    ),
    cell: ({ row }) => {
      const state = row.getValue("motion_state") as number;
      const stateMap = {
        0: "Idle",
        1: "Moving",
        2: "Waiting"
      };
      return <div>{stateMap[state as keyof typeof stateMap]}</div>;
    },
  },
  {
    accessorKey: "spare_flag",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Spare Flag" />
    ),
    cell: ({ row }) => {
      const value = row.getValue("spare_flag") as boolean;
      return <div>{value ? "Yes" : "No"}</div>;
    },
  },
  {
    accessorKey: "in_sequential_shared_points",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="In Sequential Shared Points" />
    ),
    cell: ({ row }) => {
      const value = row.getValue("in_sequential_shared_points") as boolean;
      return <div>{value ? "Yes" : "No"}</div>;
    },
  },
  {
    accessorKey: "is_deadlocked",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Is Deadlocked" />
    ),
    cell: ({ row }) => {
      const value = row.getValue("is_deadlocked") as boolean;
      return <div>{value ? "Yes" : "No"}</div>;
    },
  },
  {
    accessorKey: "last_spare_point",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Last Spare Point" />
    ),
  },
  {
    accessorKey: "active_schedule",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Active Schedule ID" />
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
