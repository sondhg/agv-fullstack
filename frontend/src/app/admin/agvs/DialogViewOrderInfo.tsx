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
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { CreateOrderZod, Order } from "@/types/Order.types";
import { zodResolver } from "@hookform/resolvers/zod";
import { Dispatch, SetStateAction, useEffect } from "react";
import { useForm } from "react-hook-form";

interface DialogViewOrderInfoProps {
  isDialogOpen: boolean;
  setIsDialogOpen: Dispatch<SetStateAction<boolean>>;
  orderToView: Order | null;
}

export function DialogViewOrderInfo({
  isDialogOpen,
  setIsDialogOpen,
  orderToView,
}: DialogViewOrderInfoProps) {
  const form = useForm({
    resolver: zodResolver(CreateOrderZod),
    defaultValues: {
      order_id: orderToView?.order_id ?? 0,
      order_date: orderToView?.order_date ?? "",
      start_time: orderToView?.start_time ?? "",
      parking_node: orderToView?.parking_node ?? 0,
      storage_node: orderToView?.storage_node ?? 0,
      workstation_node: orderToView?.workstation_node ?? 0,
    },
  });

  // Reset form when orderToView changes
  useEffect(() => {
    if (orderToView) {
      form.reset({
        order_id: orderToView.order_id,
        order_date: orderToView.order_date,
        start_time: orderToView.start_time,
        parking_node: orderToView.parking_node,
        storage_node: orderToView.storage_node,
        workstation_node: orderToView.workstation_node,
      });
    }
  }, [orderToView, form]);

  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogContent className="max-h-[80vh] min-w-[80vw] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>View Order Information</DialogTitle>
          <DialogDescription>
            Details of the order currently dispatched to this AGV.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form className="space-y-4">
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
                      <Input {...field} disabled />
                    </FormControl>
                    <FormDescription>
                      Date (yyyy-MM-dd) AGVs are expected to perform this order.
                    </FormDescription>
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
                      <Input {...field} disabled />
                    </FormControl>
                    <FormDescription>
                      Timestamp when AGVs are expected to start this order.
                    </FormDescription>
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
                      <Input {...field} type="number" disabled />
                    </FormControl>
                    <FormDescription>
                      Where AGV starts its journey and returns after finishing
                      delivery to workstation.
                    </FormDescription>
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
                      <Input {...field} type="number" disabled />
                    </FormControl>
                    <FormDescription>
                      Where AGV picks up materials.
                    </FormDescription>
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
                      <Input {...field} type="number" disabled />
                    </FormControl>
                    <FormDescription>
                      Where AGV delivers materials picked up from storage.
                    </FormDescription>
                  </FormItem>
                )}
              />
            </div>
            <div className="flex justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsDialogOpen(false)}
              >
                Close
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
