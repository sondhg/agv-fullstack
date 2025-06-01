"use client";

import { Badge } from "@/components/ui/badge";
import { createBaseColumns } from "@/components/ui/base-table-columns";
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header";
import { AGV } from "@/types/AGV.types";
import { Order } from "@/types/Order.types";
import { ColumnDef } from "@tanstack/react-table";
import { Check, X } from "lucide-react";

export const columns1 = (
  handleClickBtnDelete: (agvId: number) => void,
  handleClickActiveOrder?: (order: Order) => void,
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
          <Badge>{preferredParkingNode ? preferredParkingNode : "None"}</Badge>
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
        if (!orderInfo) return <div className="text-gray-500">None</div>;

        const order = orderInfo as Order;
        return (
          <div
            className="cursor-pointer font-medium text-blue-600 hover:text-blue-800 hover:underline"
            onClick={() => handleClickActiveOrder?.(order)}
          >
            Order {order.order_id}
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
          return <div className="text-gray-500">None</div>;
        return <div className="text-sm">{path.join(" → ")}</div>;
      },
    },
    {
      accessorKey: "remaining_path",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Remaining Path" />
      ),
      cell: ({ row }) => {
        const path = row.getValue("remaining_path") as number[];
        if (!path || path.length === 0)
          return <div className="text-gray-500">None</div>;
        return <div className="text-sm">{path.join(" → ")}</div>;
      },
    },

    {
      accessorKey: "common_nodes",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Common Nodes" />
      ),
      cell: ({ row }) => {
        const points = row.getValue("common_nodes") as number[];
        if (!points || points.length === 0)
          return <div className="text-gray-500">None</div>;
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
      accessorKey: "adjacent_common_nodes",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Adjacent Common Nodes" />
      ),
      cell: ({ row }) => {
        const points = row.getValue("adjacent_common_nodes") as number[];
        if (!points || points.length === 0)
          return <div className="text-gray-500">None</div>;
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
      accessorKey: "backup_nodes",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Backup Nodes" />
      ),
      cell: ({ row }) => {
        const value = row.getValue("backup_nodes") as Record<string, number>;
        if (Object.keys(value).length === 0) {
          return <div className="text-gray-500">None</div>;
        }
        return (
          <div className="space-y-1">
            {Object.entries(value).map(([pointInACN, sparePoint], index) => (
              <div key={index}>
                ACN <span className="font-semibold">{pointInACN}</span> → BN{" "}
                <span className="font-semibold">{sparePoint}</span>
              </div>
            ))}
          </div>
        );
      },
    },

    actionsColumn,
  ];
};
