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
      accessorKey: "residual_path",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Residual Path" />
      ),
      cell: ({ row }) => {
        const path = row.getValue("residual_path") as number[];
        if (!path || path.length === 0)
          return <div className="text-gray-500">None</div>;
        return <div className="text-sm">{path.join(" → ")}</div>;
      },
    },

    {
      accessorKey: "cp",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="CP" />
      ),
      cell: ({ row }) => {
        const points = row.getValue("cp") as number[];
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
      accessorKey: "scp",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="SCP" />
      ),
      cell: ({ row }) => {
        const points = row.getValue("scp") as number[];
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
      accessorKey: "spare_points",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="SP" />
      ),
      cell: ({ row }) => {
        const value = row.getValue("spare_points") as Record<string, number>;
        if (Object.keys(value).length === 0) {
          return <div className="text-gray-500">None</div>;
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

    actionsColumn,
  ];
};
