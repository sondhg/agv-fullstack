"use client";

import { ColumnDef } from "@tanstack/react-table";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { Schedule } from "@/types/Schedule.types";
import { AGV } from "@/types/AGV.types";
import { createBaseColumns } from "@/components/ui/base-table-columns";

export const columnsTableSchedules = (
  handleClickBtnDelete: (scheduleId: number) => void,
): ColumnDef<Schedule>[] => {
  const baseColumns = createBaseColumns<Schedule>(handleClickBtnDelete, "schedule_id");
  const [selectColumn, actionsColumn] = baseColumns;

  return [
    selectColumn,
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
      accessorKey: "initial_path",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Initial path" />
      ),
    },
    {
      accessorKey: "residual_path",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Residual Path" />
      ),
    },
    {
      accessorKey: "cp",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="CP" />
      ),
    },
    {
      accessorKey: "scp",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="SCP" />
      ),
    },
    {
      accessorKey: "sp",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="SP" />
      ),
      cell: ({ row }) => {
        const spData = row.getValue("sp");
        return (
          <pre className="whitespace-pre-wrap text-sm">
            {JSON.stringify(spData, null, 2)}
          </pre>
        );
      },
    },
    {
      accessorKey: "traveling_info",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Traveling Info" />
      ),
      cell: ({ row }) => {
        const travelingInfo = row.getValue("traveling_info");
        return (
          <pre className="whitespace-pre-wrap text-sm">
            {JSON.stringify(travelingInfo, null, 2)}
          </pre>
        );
      },
    },
    {
      accessorKey: "assigned_agv",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Assigned AGV" />
      ),
      cell: ({ row }) => {
        const agv = row.getValue("assigned_agv") as AGV | null;
        if (!agv) return <div className="text-gray-500">No AGV Assigned</div>;

        const stateColor = {
          0: "bg-gray-200", // Idle
          1: "bg-green-200", // Moving
          2: "bg-yellow-200", // Waiting
        };

        return (
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${stateColor[agv.motion_state]}`} />
            <div>
              <div className="font-medium">AGV {agv.agv_id}</div>
              <div className="text-sm text-gray-500">
                Parking Node: {agv.preferred_parking_node}
                {agv.current_node !== null && ` • Current: ${agv.current_node}`}
              </div>
            </div>
          </div>
        );
      },
    },
    actionsColumn,
  ];
};
