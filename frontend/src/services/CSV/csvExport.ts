import { Order } from "@/types/Order.types";

export const handleExportCSV = (data: Order[]) => {
  const headers = [
    "order_id",
    "order_date",
    "start_time",
    "start_point",
    "end_point",
    "load_name",
    "load_amount",
    "load_weight",
    "user_name",
  ];

  const csvRows = [
    headers.join(","), // header row
    ...data.map((order) =>
      [
        order.order_id,
        order.order_date,
        order.start_time,
        order.start_point,
        order.end_point,
        order.load_name,
        order.load_amount,
        order.load_weight,
        order.user_name,
      ].join(","),
    ),
  ];

  const csvContent = csvRows.join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", "orders_exported.csv");
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
