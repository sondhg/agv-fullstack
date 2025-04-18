"use client";

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
import { createAGV } from "@/services/APIs/agvsAPI";
import { CreateAGVDto } from "@/types/AGV.types";
import { convertStringToNumber } from "@/utils/conversionUtils";
import { zodResolver } from "@hookform/resolvers/zod";
import { CirclePlus } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const formSchema = z.object({
  agv_id: z.string().min(1).regex(/^\d+$/, { message: "Must be integer" }),
  preferred_parking_node: z
    .string()
    .min(1)
    .regex(/^\d+$/, { message: "Must be integer" }),
});

interface FormCreateAGVsProps {
  isDialogOpen: boolean;
  setIsDialogOpen: (value: boolean) => void;
  fetchListData: () => void;
}

export function DialogFormCreateAGVs({
  isDialogOpen,
  setIsDialogOpen,
  fetchListData,
}: FormCreateAGVsProps) {
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      agv_id: "",
      preferred_parking_node: "",
    },
    mode: "onChange",
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    const createDto: CreateAGVDto = {
      agv_id: convertStringToNumber(values.agv_id),
      preferred_parking_node: convertStringToNumber(
        values.preferred_parking_node,
      ),
    };

    try {
      const data = await createAGV(createDto);
      if (data) {
        toast({
          title: "AGV created successfully",
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
      console.error("Error creating AGV:", error);
      toast({
        title: "AGV creation failed",
        description: "That AGV ID already exists.",
      });
    }
  }

  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogTrigger asChild>
        <Button variant="default">
          <CirclePlus />
          Create AGV
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create new AGV</DialogTitle>
          <DialogDescription>
            Add a new AGV with its preferred parking node.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="agv_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>AGV ID</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter integer from 1 to 999"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Unique ID you assign to this AGV.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="preferred_parking_node"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Preferred Parking Node</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter node number" {...field} />
                  </FormControl>
                  <FormDescription>
                    The preferred parking node for this AGV.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" disabled={!form.formState.isValid}>
              Submit
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
