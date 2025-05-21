import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { createMultipleOrdersBatch } from "@/services/APIs/ordersAPI";
import { ListPlus } from "lucide-react";
import { toast } from "sonner";
import { generateExampleOrders } from "./OrdersUtils";

interface OrdersExampleGeneratorProps {
  fetchListData: () => Promise<void>;
}

export function OrdersExampleGenerator({
  fetchListData,
}: OrdersExampleGeneratorProps) {
  // Handle creating example orders directly
  const handleCreateExampleOrders = async (
    example: "example1and2" | "example3",
  ) => {
    try {
      const orders = generateExampleOrders(example);
      await createMultipleOrdersBatch(orders);
      toast.success(`Created ${orders.length} example orders successfully`);
      await fetchListData();
    } catch (error) {
      console.error("Failed to create example orders:", error);
      toast.error("Failed to create example orders. Please try again.");
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          <ListPlus className="mr-2 h-4 w-4" />
          Create Example Orders
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem
          onClick={() => handleCreateExampleOrders("example1and2")}
        >
          Example 1 and 2
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleCreateExampleOrders("example3")}>
          Example 3
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
