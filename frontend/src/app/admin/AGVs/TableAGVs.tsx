import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "sonner";
import { deleteAGV } from "@/services/APIs/agvAPI";

interface TableAGVsProps {
  listData: Array<{
    agv_id: number;
    guidance_type: string;
    max_battery: number;
    max_load: number;
    max_speed: number;
    is_connected: boolean;
    is_busy: boolean;
    is_active: boolean;
  }>;
  fetchListData: () => Promise<void>;
}

export function TableAGVs(props: TableAGVsProps) {
  const { listData, fetchListData } = props;

  // Sort listData by agv_id in ascending order
  const sortedListAGVs = [...listData].sort((a, b) => a.agv_id - b.agv_id);

  const handleDelete = async (agvId: number) => {
    try {
      await deleteAGV(agvId);
      await fetchListData();
      toast.warning("Deleted AGV from team!");
    } catch (error) {
      console.error("Failed to delete AGV:", error);
    }
  };

  const tableHeaders = [
    { label: "AGV ID", key: "agv_id" },
    { label: "Guidance type", key: "guidance_type" },
    { label: "Max battery", key: "max_battery" },
    { label: "Max load", key: "max_load" },
    { label: "Max speed", key: "max_speed" },
    { label: "Is connected?", key: "is_connected" },
    { label: "Is busy?", key: "is_busy" },
    { label: "Is active?", key: "is_active" },
    { label: "Action", key: null },
  ];

  return (
    <div className="relative min-h-96">
      <div className="rounded-md border-2">
        <Table>
          <TableHeader>
            <TableRow>
              {tableHeaders.map((header, index) => (
                <TableHead
                  key={index}
                  className={header.label === "AGV ID" ? "w-[120px]" : ""}
                >
                  {header.label}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.isArray(sortedListAGVs) && sortedListAGVs.length > 0 ? (
              sortedListAGVs.map((item, index) => (
                <TableRow key={index}>
                  {tableHeaders.map((header, cellIndex) => (
                    <TableCell
                      key={cellIndex}
                      className={header.key === "agv_id" ? "font-medium" : ""}
                    >
                      {header.key === "is_connected" ||
                      header.key === "is_busy" ||
                      header.key === "is_active" ? (
                        item[header.key] ? (
                          "Yes"
                        ) : (
                          "No"
                        )
                      ) : header.label === "Action" ? (
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                variant="destructive"
                                onClick={() => handleDelete(item.agv_id)}
                              >
                                Delete
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Remove this AGV from team</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      ) : header.key ? (
                        item[header.key as keyof typeof item]
                      ) : null}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={tableHeaders.length}>
                  No data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
