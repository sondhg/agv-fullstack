"use client";

import { ColumnDef } from "@tanstack/react-table";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { Schedule } from "@/types/Schedule.types";
import { AGV } from "@/types/AGV.types";
import { createBaseColumns } from "@/components/ui/base-table-columns";

export const columnsTableSchedules = (
  handleClickBtnDelete: (scheduleId: number) => void,
): ColumnDef<Schedule>[] => {
  const baseColumns = createBaseColumns<Schedule>(
    handleClickBtnDelete,
    "schedule_id",
  );
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
      accessorKey: "assigned_agv",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Assigned AGV" />
      ),
      cell: ({ row }) => {
        const agv = row.getValue("assigned_agv") as AGV | null;
        if (!agv) return <div className="text-gray-500">No AGV Assigned</div>;

        return (
          <div className="flex items-center gap-2">
            <div>
              <div className="font-medium">AGV {agv.agv_id}</div>
            </div>
          </div>
        );
      },
    },
    actionsColumn,
  ];
};
