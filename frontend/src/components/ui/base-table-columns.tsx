import { ColumnDef } from "@tanstack/react-table";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

export function createBaseColumns<T extends { [key: string]: any }>(
  handleClickBtnDelete: (id: number) => void,
  idKey: keyof T
): ColumnDef<T>[] {
  return [
    {
      id: "select",
      header: ({ table }) => (
        <Checkbox
          checked={
            table.getIsAllPageRowsSelected() ||
            (table.getIsSomePageRowsSelected() && "indeterminate")
          }
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
        />
      ),
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const item = row.original;
        return (
          <Button
            variant={"destructive"}
            onClick={() => handleClickBtnDelete(item[idKey])}
          >
            <Trash2 />
          </Button>
        );
      },
    },
  ];
}