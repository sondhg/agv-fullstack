import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { simulateUpdateAgvPosition } from "@/services/APIs/agvsAPI";
import { zodResolver } from "@hookform/resolvers/zod";
import { RefreshCw } from "lucide-react";
import { RefObject, useCallback, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { ButtonStepSimulation } from "./ButtonStepSimulation";

/**
 * Form schema for AGV position update simulation
 * Validates that both fields are positive integers
 */
const formSchema = z.object({
  agv_id: z.string().min(1, "AGV ID is required").regex(/^\d+$/, {
    message: "AGV ID must be a positive integer",
  }),
  current_node: z.string().min(1, "Current node is required").regex(/^\d+$/, {
    message: "Current node must be a positive integer",
  }),
});

type FormValues = z.infer<typeof formSchema>;

/**
 * Form component for simulating AGV position updates
 *
 * @param props.onUpdateSuccess - Callback function to run after successful position update
 * @param props.stepSimulationRef - Reference to the ButtonStepSimulation component for keyboard shortcuts
 */
export const FormSimulateUpdateAgvPosition = ({
  onUpdateSuccess,
  stepSimulationRef,
  hasDispatchedOrders = false, // Add this prop with default value
}: {
  onUpdateSuccess?: () => Promise<void>;
  stepSimulationRef?: RefObject<HTMLButtonElement>;
  hasDispatchedOrders?: boolean;
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  // Reference to store the reset function from ButtonStepSimulation
  const resetSimulationRef = useRef<(() => void) | null>(null);

  // Initialize form with React Hook Form and Zod validation
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      agv_id: "",
      current_node: "",
    },
    mode: "onChange",
  });

  /**
   * Store the reset function from ButtonStepSimulation
   */
  const handleResetRef = useCallback((resetFn: () => void) => {
    resetSimulationRef.current = resetFn;
  }, []);

  /**
   * Reset the simulation when the reset button is clicked
   */
  const handleReset = () => {
    if (resetSimulationRef.current) {
      resetSimulationRef.current();
    }
  };

  /**
   * Handle form submission
   * Sends the AGV ID and current node to the API
   *
   * @param values - Form values containing agv_id and current_node
   */
  const onSubmit = async (values: FormValues) => {
    setIsSubmitting(true);
    try {
      // Convert string values to numbers for the API
      const agvId = parseInt(values.agv_id, 10);
      const currentNode = parseInt(values.current_node, 10);

      await simulateUpdateAgvPosition(agvId, currentNode);
      toast.success("AGV position updated successfully");
      // form.reset(); // Empty the input fields after successful submission

      // Call the onUpdateSuccess callback if provided
      if (onUpdateSuccess) {
        await onUpdateSuccess();
      }
    } catch (error) {
      console.error("Error updating AGV position:", error);
      toast.error("Failed to update AGV position");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <div className="grid grid-cols-3 gap-2">
        <div className="col-span-2">
          <CardHeader>
            <CardTitle>Simulate AGV Position Update</CardTitle>
          </CardHeader>
          <CardContent>
            <div>
              <div>
                <Form {...form}>
                  <form
                    onSubmit={form.handleSubmit(onSubmit)}
                    className="space-y-4"
                  >
                    <div className="flex flex-col gap-4 md:flex-row">
                      <FormField
                        control={form.control}
                        name="agv_id"
                        render={({ field }) => (
                          <FormItem className="flex-1">
                            <FormLabel>AGV ID</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="Enter ID of AGV"
                                type="text"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="current_node"
                        render={({ field }) => (
                          <FormItem className="flex-1">
                            <FormLabel>Current Node</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="Enter current position"
                                type="text"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <Button
                        type="submit"
                        className="w-full md:w-auto md:self-end"
                        disabled={isSubmitting || !form.formState.isValid}
                      >
                        {isSubmitting ? "Updating..." : "Update Position"}
                      </Button>
                    </div>
                  </form>
                </Form>
              </div>
            </div>
          </CardContent>
        </div>
        <div className="col-span-1 m-2 flex flex-col justify-center gap-4">
          <ButtonStepSimulation
            onUpdateSuccess={onUpdateSuccess}
            onResetRef={handleResetRef}
            ref={stepSimulationRef}
            hasDispatchedOrders={hasDispatchedOrders}
          />
          <Button onClick={handleReset} variant="destructive" className="w-full">
            <RefreshCw className="mr-2 h-4 w-4" />
            Reset Simulation
          </Button>
        </div>
      </div>
    </Card>
  );
};
