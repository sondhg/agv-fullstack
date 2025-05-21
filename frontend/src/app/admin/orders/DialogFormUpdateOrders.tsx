"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
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
import { updateOrder } from "@/services/APIs/ordersAPI";
import { CreateOrderZod, Order } from "@/types/Order.types";
import { zodResolver } from "@hookform/resolvers/zod";
import { Dispatch, SetStateAction, useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

interface DialogFormUpdateOrdersProps {
  isDialogOpen: boolean;
  setIsDialogOpen: Dispatch<SetStateAction<boolean>>;
  fetchListData: () => Promise<void>;
  orderToUpdate: Order | null;
}

export function DialogFormUpdateOrders({
  isDialogOpen,
  setIsDialogOpen,
  fetchListData,
  orderToUpdate,
}: DialogFormUpdateOrdersProps) {
  const form = useForm({
    resolver: zodResolver(CreateOrderZod),
    defaultValues: {
      order_id: orderToUpdate?.order_id ?? 0,
      order_date: orderToUpdate?.order_date ?? "",
      start_time: orderToUpdate?.start_time ?? "",
      parking_node: orderToUpdate?.parking_node ?? 0,
      storage_node: orderToUpdate?.storage_node ?? 0,
      workstation_node: orderToUpdate?.workstation_node ?? 0,
    },
  });
  // Reset form when orderToUpdate changes
  useEffect(() => {
    if (orderToUpdate) {
      form.reset({
        order_id: orderToUpdate.order_id,
        order_date: orderToUpdate.order_date,
        start_time: orderToUpdate.start_time,
        parking_node: orderToUpdate.parking_node,
        storage_node: orderToUpdate.storage_node,
        workstation_node: orderToUpdate.workstation_node,
      });
    }
  }, [orderToUpdate, form]);

  type FormValues = {
    order_id: number;
    order_date: string;
    start_time: string;
    parking_node: number;
    storage_node: number;
    workstation_node: number;
  };

  const onSubmit = async (values: FormValues) => {
    try {
      await updateOrder(values.order_id, values);
      toast.success("Order updated successfully");
      setIsDialogOpen(false);
      fetchListData();
    } catch (error) {
      console.error("Error updating order:", error);
      toast.error("Failed to update order. Please try again.");
    }
  };

  return (
    <>
      {" "}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-h-[80vh] min-w-[80vw] overflow-y-auto">
          {" "}
          <DialogHeader>
            <DialogTitle>Update Order</DialogTitle>
            <DialogDescription>
              Update order details for your AGV.
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            {" "}
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-4">
                <FormField
                  control={form.control}
                  name="order_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Order ID</FormLabel>
                      <FormControl>
                        <Input {...field} disabled />
                      </FormControl>
                      <FormDescription>
                        Unique ID assigned to this order.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />{" "}
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
                />{" "}
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
                        <Input {...field} type="number" />
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
                        <Input {...field} type="number" />
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
                        <Input {...field} type="number" />
                      </FormControl>
                      <FormDescription>
                        Where AGV delivers materials picked up from storage.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>{" "}
              <div className="space-x-5">
                <Button type="submit" disabled={!form.formState.isValid}>
                  Confirm Update
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsDialogOpen(false);
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </>
  );
}
