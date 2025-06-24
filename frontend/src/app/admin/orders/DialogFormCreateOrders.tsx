"use client";

import { DialogMap } from "@/app/layout/DialogMap";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useFormDialog } from "@/hooks/useFormDialog";
import { createOrder } from "@/services/APIs/ordersAPI";
import { CreateOrderDto } from "@/types/Order.types";
import { convertStringToNumber } from "@/utils/conversionUtils";
import { CirclePlus } from "lucide-react";
import { z } from "zod";

const formSchema = z.object({
  order_id: z.string().min(1).regex(/^\d+$/, { message: "Must be integer" }),
  order_date: z
    .string()
    .regex(/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/, {
      message: "Date must be in the format yyyy-mm-dd.",
    }),
  start_time: z.string().regex(/^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$/, {
    message: "Time must be in 23h format hh:mm:ss",
  }),
  parking_node: z
    .string()
    .min(1)
    .regex(/^\d+$/, { message: "Must be integer" }),
  storage_node: z
    .string()
    .min(1)
    .regex(/^\d+$/, { message: "Must be integer" }),
  workstation_node: z
    .string()
    .min(1)
    .regex(/^\d+$/, { message: "Must be integer" }),
});

interface FormCreateOrdersProps {
  isDialogOpen: boolean;
  setIsDialogOpen: (value: boolean) => void;
  fetchListData: () => void;
}

export function DialogFormCreateOrders({
  isDialogOpen,
  setIsDialogOpen,
  fetchListData,
}: FormCreateOrdersProps) {
  const { form, handleSubmit } = useFormDialog({
    defaultValues: {
      order_id: "",
      order_date: "",
      start_time: "",
      parking_node: "",
      storage_node: "",
      workstation_node: "",
    },
    schema: formSchema,
    onSubmit: async (values) => {
      const createDto: CreateOrderDto = {
        order_id: convertStringToNumber(values.order_id),
        order_date: values.order_date,
        start_time: values.start_time,
        parking_node: convertStringToNumber(values.parking_node),
        storage_node: convertStringToNumber(values.storage_node),
        workstation_node: convertStringToNumber(values.workstation_node),
      };
      await createOrder(createDto);
    },
    successMessage: "Order created successfully",
    errorMessage: "Order creation failed",
    onSuccess: () => {
      fetchListData();
      setIsDialogOpen(false);
    },
  });

  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogTrigger asChild>
        <Button variant="default">
          <CirclePlus />
          Create order
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[80vh] min-w-[80vw] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create new order</DialogTitle>
          <DialogDescription>Add inputs for your AGV here.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-4">
              <FormField
                control={form.control}
                name="order_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Order ID</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter integer from 1 to 999"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Unique ID you assign to this order.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="order_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Order Date</FormLabel>
                    <FormControl>
                      <Input placeholder="Example: 2022-12-31" {...field} />
                    </FormControl>
                    <FormDescription>
                      Date (yyyy-MM-dd) you expect AGVs to perform this order.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="start_time"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Start Time</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter in format HH:mm:ss"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Timestamp of the Order Date you selected that you expect
                      AGVs to perform this order.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="parking_node"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Parking Node</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormDescription>
                      Where AGV starts its journey and returns after finishing
                      delivery to workstation.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="storage_node"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Storage Node</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormDescription>
                      Where AGV picks up materials.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="workstation_node"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Workstation Node</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormDescription>
                      Where AGV delivers materials picked up from storage.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="space-x-5">
              <Button type="submit" disabled={!form.formState.isValid}>
                Submit
              </Button>
              <DialogMap />
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
