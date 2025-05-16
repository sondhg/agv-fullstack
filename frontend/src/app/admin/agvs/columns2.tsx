"use client";

import { Badge } from "@/components/ui/badge";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { AGV } from "@/types/AGV.types";
import { ColumnDef } from "@tanstack/react-table";

export const columns2 = (): ColumnDef<AGV>[] => {
  return [
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
      accessorKey: "previous_node",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Previous Node" />
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
      accessorKey: "direction_change",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Direction Change" />
      ),
      cell: ({ row }) => {
        const state = row.getValue("direction_change") as number;
        const stateMap = {
          0: "Go straight",
          1: "Turn around",
          2: "Turn left",
          3: "Turn right",
          4: "Stay still",
        };
        return (
          <Badge
            variant={
              state === 0
                ? "default"
                : state === 1
                  ? "destructive"
                  : state === 2
                    ? "secondary"
                    : "outline"
            }
          >
            {stateMap[state as keyof typeof stateMap]}
          </Badge>
        );
      },
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
          2: "Waiting",
        };
        return (
          <Badge
            variant={
              state === 0
                ? "secondary"
                : state === 1
                  ? "default"
                  : "destructive"
            }
          >
            {stateMap[state as keyof typeof stateMap]}
          </Badge>
        );
      },
    },
  ];
};
