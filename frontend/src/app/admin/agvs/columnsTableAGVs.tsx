"use client";

import { Badge } from "@/components/ui/badge";
import { createBaseColumns } from "@/components/ui/base-table-columns";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { AGV } from "@/types/AGV.types";
import { Order } from "@/types/Order.types";
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
      accessorKey: "active_order_info",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Active Order" />
      ),
      cell: ({ row }) => {
        const orderInfo = row.getValue("active_order_info");
        if (!orderInfo)
          return <div className="text-gray-500">No Active Order</div>;
        return (
          <div>
            <div className="font-medium">
              Order {(orderInfo as Order).order_id}
            </div>
            <div className="text-sm text-gray-500">
              Parking: {(orderInfo as Order).parking_node} → Storage:{" "}
              {(orderInfo as Order).storage_node} → Workstation:{" "}
              {(orderInfo as Order).workstation_node}
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: "initial_path",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Initial Path" />
      ),
      cell: ({ row }) => {
        const path = row.getValue("initial_path") as number[];
        if (!path || path.length === 0)
          return <div className="text-gray-500">No path</div>;
        return <div className="text-sm">{path.join(" → ")}</div>;
      },
    },
    {
      accessorKey: "residual_path",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Residual Path" />
      ),
      cell: ({ row }) => {
        const path = row.getValue("residual_path") as number[];
        if (!path || path.length === 0)
          return <div className="text-gray-500">No path</div>;
        return <div className="text-sm">{path.join(" → ")}</div>;
      },
    },
    {
      accessorKey: "cp",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Shared Points (CP)" />
      ),
      cell: ({ row }) => {
        const points = row.getValue("cp") as number[];
        if (!points || points.length === 0)
          return <div className="text-gray-500">No shared points</div>;
        return (
          <div className="text-sm">
            {points.map((point) => (
              <Badge key={point} variant="outline" className="mr-1">
                {point}
              </Badge>
            ))}
          </div>
        );
      },
    },
    {
      accessorKey: "scp",
      header: ({ column }) => (
        <DataTableColumnHeader
          column={column}
          title="Sequential Points (SCP)"
        />
      ),
      cell: ({ row }) => {
        const points = row.getValue("scp") as number[];
        if (!points || points.length === 0)
          return <div className="text-gray-500">No sequential points</div>;
        return (
          <div className="text-sm">
            {points.map((point) => (
              <Badge key={point} variant="outline" className="mr-1">
                {point}
              </Badge>
            ))}
          </div>
        );
      },
    },
    actionsColumn,
  ];
};
