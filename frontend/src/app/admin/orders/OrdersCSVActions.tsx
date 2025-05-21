import { Button } from "@/components/ui/button";
import { handleExportCSV } from "@/services/CSV/csvExport";
import { useCSVImport } from "@/services/CSV/useCSVImport";
import { Order } from "@/types/Order.types";
import { FileDown, FileUp } from "lucide-react";
import { useRef } from "react";
import { DialogInstructionsCSV } from "./DialogInstructionsCSV";

interface OrdersCSVActionsProps {
  listOrders: Order[];
  fetchListData: () => Promise<void>;
}

export function OrdersCSVActions({
  listOrders,
  fetchListData,
}: OrdersCSVActionsProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { handleImportCSV } = useCSVImport();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleImportCSV(file, fetchListData).finally(() => {
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      });
    }
  };

  return (
    <>
      <Button onClick={() => fileInputRef.current?.click()}>
        <FileUp />
        Import CSV
      </Button>
      <input
        type="file"
        ref={fileInputRef}
        accept=".csv"
        className="hidden"
        onChange={handleFileChange}
      />
      <Button variant={"secondary"} onClick={() => handleExportCSV(listOrders)}>
        <FileDown />
        Export CSV
      </Button>
      <DialogInstructionsCSV />
    </>
  );
}
