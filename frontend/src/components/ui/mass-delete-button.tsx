import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import { toast } from "sonner";

interface MassDeleteButtonProps {
  selectedIds: number[];
  onDelete: (ids: number[]) => Promise<void>;
  itemName?: string;
  onSuccess?: () => void;
  resetSelection?: () => void;
}

export function MassDeleteButton({
  selectedIds,
  onDelete,
  itemName = "items",
  onSuccess,
  resetSelection
}: MassDeleteButtonProps) {
  const handleMassDelete = async () => {
    if (selectedIds.length === 0) {
      toast.error(`Please select at least one ${itemName} to delete`);
      return;
    }

    try {
      await onDelete(selectedIds);
      toast.success(`${selectedIds.length} ${itemName} deleted successfully`);
      resetSelection?.(); // Reset selection state after successful deletion
      onSuccess?.(); // Fetch new data after successful deletion
    } catch (error) {
      if (error instanceof Response) {
        const errorData = await error.json();
        toast.error(errorData.error || `Failed to delete ${itemName}`);
      } else {
        toast.error(`Failed to delete ${itemName}`);
      }
      console.error("Mass delete error:", error);
    }
  };

  return (
    <Button
      variant="destructive"
      onClick={handleMassDelete}
      disabled={selectedIds.length === 0}
    >
      <Trash2 className="mr-2 h-4 w-4" />
      Mass Delete {itemName}
    </Button>
  );
}