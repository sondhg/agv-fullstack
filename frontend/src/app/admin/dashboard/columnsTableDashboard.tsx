"use client";

import { ColumnDef } from "@tanstack/react-table";

import { Checkbox } from "@/components/ui/checkbox";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { WebSocketData } from "@/types/WebSocket.types";

export const columnsTableDashboard: ColumnDef<WebSocketData>[] = [
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
    accessorKey: "car_id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Car ID" />
    ),
  },
  {
    accessorKey: "agv_state",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="State" />
    ),
  },
  {
    accessorKey: "agv_speed",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Speed" />
    ),
  },
  {
    accessorKey: "agv_battery",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Battery" />
    ),
    cell: ({ row }) => {
      const agv_battery = parseFloat(row.getValue("agv_battery"));
      return <div className="font-medium">{agv_battery}%</div>;
    },
  },
  {
    accessorKey: "previous_waypoint",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Previous Waypoint" />
    ),
  },
  {
    accessorKey: "next_waypoint",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Next Waypoint" />
    ),
  },
  {
    accessorKey: "time_stamp",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Timestamp" />
    ),
  },
  {
    accessorKey: "distance_sum",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Distance Sum" />
    ),
  },
  {
    accessorKey: "distance",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Distance" />
    ),
  },
];
