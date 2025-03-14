"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { createAGV } from "@/services/APIs/agvAPI";
import { agvIDs, guidanceTypes } from "@/utils/arraysUsedOften";
import { convertStringToNumber } from "@/utils/conversionUtils";
import { zodResolver } from "@hookform/resolvers/zod";
import { CirclePlus } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { CreateAgvDto } from "../../../types/AGV.types";

const formSchema = z.object({
  agv_id: z
    .string()
    .min(1)
    .max(1)
    .refine((value) => convertStringToNumber(value)),
  max_speed: z
    .string()
    .min(1)
    .max(2)
    .refine((value) => convertStringToNumber(value)),
  max_battery: z
    .string()
    .min(1)
    .max(3)
    .refine((value) => convertStringToNumber(value)),
  max_load: z
    .string()
    .min(1)
    .max(2)
    .refine((value) => convertStringToNumber(value)),
  guidance_type: z.string(),
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
      max_speed: "",
      max_battery: "",
      max_load: "",
      guidance_type: "",
    },
    mode: "onChange",
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    const createDto: CreateAgvDto = {
      agv_id: convertStringToNumber(values.agv_id),
      max_speed: convertStringToNumber(values.max_speed),
      max_battery: convertStringToNumber(values.max_battery),
      max_load: convertStringToNumber(values.max_load),
      guidance_type: values.guidance_type,
    };

    try {
      const data = await createAGV(createDto);
      if (data) {
        console.log("data", data);
        toast({
          title: "AGV added successfully",
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
      console.log("Error creating AGV:", error);
      toast({
        title: "AGV creation failed",
        description: "That agv_id already exist.",
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
      <DialogContent className="max-h-[80vh] min-w-[80vw] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create new AGV</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
              <FormField
                control={form.control}
                name="agv_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>AGV ID</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      {...field}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select an AGV ID" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {agvIDs.map((item) => (
                          <SelectItem key={item} value={item}>
                            {item}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>Select AGV ID</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="guidance_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Guidance type</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      {...field}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a guidance type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {guidanceTypes.map((item) => (
                          <SelectItem key={item} value={item}>
                            {item}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>Select guidance type</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="max_battery"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Max battery</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter number from 1 to 100"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Enter max battery capacity
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="max_load"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Max load</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter number from 1 to 50"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Enter max load weight that can be carried by this AGV
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="max_speed"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Max speed</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter number from 1 to 30"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Enter max speed limit (unit: m/s)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <Button type="submit" disabled={!form.formState.isValid}>
              Submit
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
