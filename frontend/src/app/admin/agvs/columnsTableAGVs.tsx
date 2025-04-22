"use client";

import { Badge } from "@/components/ui/badge";
import { createBaseColumns } from "@/components/ui/base-table-columns";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { AGV } from "@/types/AGV.types";
import { Schedule } from "@/types/Schedule.types";
import { ColumnDef } from "@tanstack/react-table";
import { Check, X } from "lucide-react";

export const columnsTableAGVs = (
  handleClickBtnDelete: (agvId: number) => void,
): ColumnDef<AGV>[] => {
  const baseColumns = createBaseColumns<AGV>(handleClickBtnDelete, "agv_id");
  const [selectColumn, actionsColumn] = baseColumns;

  return [
    selectColumn,
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
      cell: ({ row }) => {
        const preferredParkingNode = row.getValue(
          "preferred_parking_node",
        ) as number;
        return (
          <Badge>
            {preferredParkingNode ? preferredParkingNode : "No Parking Node"}
          </Badge>
        );
      },
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
    {
      accessorKey: "spare_flag",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Spare Flag" />
      ),
      cell: ({ row }) => {
        const value = row.getValue("spare_flag") as boolean;
        return (
          <div>{value ? <Check color="#00ff00" /> : <X color="#ff0000" />}</div>
        );
      },
    },
    {
      accessorKey: "spare_points",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Spare Points" />
      ),
      cell: ({ row }) => {
        const value = row.getValue("spare_points") as Record<string, number>;
        if (Object.keys(value).length === 0) {
          return <div className="text-gray-500">No SP</div>;
        }
        return (
          <div className="space-y-1">
            {Object.entries(value).map(([pointInSCP, sparePoint], index) => (
              <div key={index}>
                SCP <span className="font-semibold">{pointInSCP}</span> → SP{" "}
                <span className="font-semibold">{sparePoint}</span>
              </div>
            ))}
          </div>
        );
      },
    },
    {
      accessorKey: "active_schedule",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Active Schedule" />
      ),
      cell: ({ row }) => {
        const schedule = row.getValue("active_schedule");
        if (!schedule)
          return <div className="text-gray-500">No Active Schedule</div>;
        return (
          <div>
            <div className="font-medium">
              Schedule {(schedule as Schedule).schedule_id}
            </div>
            <div className="text-sm text-gray-500">
              Parking: {(schedule as Schedule).parking_node} → Storage:{" "}
              {(schedule as Schedule).storage_node} → Workstation:{" "}
              {(schedule as Schedule).workstation_node}
            </div>
          </div>
        );
      },
    },
    actionsColumn,
  ];
};
