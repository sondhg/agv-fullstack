import { createMultipleOrdersBatch } from "@/services/APIs/ordersAPI";
import { CreateOrderDto } from "@/types/Order.types";
import Papa from "papaparse";
import { toast } from "sonner";

interface CsvRow {
  order_id: number;
  order_date: string;
  start_time: string;
  parking_node: number;
  storage_node: number;
  workstation_node: number;
}

const mapToOrderDto = (row: CsvRow): CreateOrderDto | null => {
  if (
    row.order_id &&
    row.order_date &&
    row.start_time &&
    row.parking_node &&
    row.storage_node &&
    row.workstation_node
  ) {
    try {
      return {
        order_id: row.order_id,
        order_date: row.order_date,
        start_time: row.start_time,
        parking_node: row.parking_node,
        storage_node: row.storage_node,
        workstation_node: row.workstation_node,
      };
    } catch (err) {
      console.error(`Row validation failed: ${JSON.stringify(row)}`, err);
      return null;
    }
  }
  console.error(`Row missing required fields: ${JSON.stringify(row)}`);
  return null;
};

export const useCSVImport = () => {

  const handleImportCSV = async (file: File, fetchListData: () => void) => {
    // Parse the CSV file
    Papa.parse(file, {
      complete: async (result) => {
        const validOrders: CreateOrderDto[] = [];
        const invalidRows: CsvRow[] = [];

        // Process each row and map to valid order
        result.data.forEach((row) => {
          const order = mapToOrderDto(row as CsvRow);
          if (order) {
            validOrders.push(order);
          } else {
            invalidRows.push(row as CsvRow);
          }
        });

        // Provide feedback for invalid rows
        if (invalidRows.length > 0) {
          toast.error(`Skipped ${invalidRows.length} invalid rows.`);
        }

        // If valid orders exist, send them to the API
        if (validOrders.length > 0) {
          try {
            await createMultipleOrdersBatch(validOrders);
            toast.success("Orders imported successfully.");
            fetchListData(); // Refresh data after import
          } catch (error) {
            console.error("Failed to import orders:", error);
            toast.error("Failed to import orders. Please try again.");
          }
        }
      },
      error: (error) => {
        console.error("CSV parsing error:", error);
        toast.error("Failed to parse CSV. Please check the file format.");
      },
      header: true, // Assuming the first row contains headers
      skipEmptyLines: true, // Skip empty lines
    });
  };

  return { handleImportCSV };
};
