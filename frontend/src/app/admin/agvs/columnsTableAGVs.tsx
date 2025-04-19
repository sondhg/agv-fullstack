"use client";

import { ColumnDef } from "@tanstack/react-table";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { AGV } from "@/types/AGV.types";
import { Schedule } from "@/types/Schedule.types";
import { createBaseColumns } from "@/components/ui/base-table-columns";

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
      accessorKey: "spare_points",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Spare Points" />
      ),
      cell: ({ row }) => {
        const value = row.getValue("spare_points") as Record<string, number>;
        return (
          <div>
            {Object.keys(value).length > 0
              ? "Has spare points"
              : "No spare points"}
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
