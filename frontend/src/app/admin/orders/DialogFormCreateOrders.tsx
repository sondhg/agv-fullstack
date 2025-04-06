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
import { useToast } from "@/hooks/use-toast";
import { createOrder } from "@/services/APIs/ordersAPI";
import { CreateOrderDto } from "@/types/Order.types";
import { convertStringToNumber } from "@/utils/conversionUtils";
import { zodResolver } from "@hookform/resolvers/zod";
import { CirclePlus } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

// import { vi } from "date-fns/locale";

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
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      order_id: "",
      order_date: "",
      start_time: "",
      parking_node: "",
      storage_node: "",
      workstation_node: "",
    },
    mode: "onChange",
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    const createDto: CreateOrderDto = {
      order_id: convertStringToNumber(values.order_id),
      order_date: values.order_date,
      start_time: values.start_time,
      parking_node: convertStringToNumber(values.parking_node),
      storage_node: convertStringToNumber(values.storage_node),
      workstation_node: convertStringToNumber(values.workstation_node),
    };

    try {
      const data = await createOrder(createDto);
      if (data) {
        console.log("data", data);
        toast({
          title: "Order created successfully",
          description: (
            <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
              <code className="text-white">
                {JSON.stringify(data, null, 2)}
              </code>
            </pre>
          ),
        });
        fetchListData();
        setIsDialogOpen(false);
      }
    } catch (error) {
      console.log("Error creating order:", error);
      toast({
        title: "Order creation failed",
        description: "That order_id already exist.",
      });
    }
  }

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
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
                      Parking node of this order's route.
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
                      <Input placeholder="Enter load name" {...field} />
                    </FormControl>
                    <FormDescription>
                      Storage node of this order's route.
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
                      Workstation node of this order's route.
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
