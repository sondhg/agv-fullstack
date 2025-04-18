"use client";

import { ColumnDef } from "@tanstack/react-table";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { Schedule } from "@/types/Schedule.types";
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
    actionsColumn,
  ];
};
