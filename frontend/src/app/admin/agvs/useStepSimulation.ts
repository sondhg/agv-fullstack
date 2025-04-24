import { simulateUpdateAgvPosition } from "@/services/APIs/agvsAPI";
import { useState } from "react";
import { toast } from "sonner";
import { simulationSteps } from "./simulationSteps";

export const useStepSimulation = (onUpdateSuccess?: () => Promise<void>) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);

  const handleNextStep = async () => {
    if (isSimulating) return;

    setIsSimulating(true);
    try {
      const step = simulationSteps[currentStepIndex];
      await simulateUpdateAgvPosition(step.agv_id, step.current_node);

      // Show toast for each AGV movement
      toast.success(`Moved AGV ${step.agv_id} to node ${step.current_node}`);

      if (onUpdateSuccess) {
        await onUpdateSuccess();
      }

      // Update step index and check for cycle completion
      const nextIndex = (currentStepIndex + 1) % simulationSteps.length;
      setCurrentStepIndex(nextIndex);

      if (nextIndex === 0) {
        toast.info(
          `Simulation done. Click "Dispatch orders to AGVs" to start again.`,
        );
      }
    } catch (error) {
      toast.error("Failed to simulate step");
      console.error("Simulation step failed:", error);
    } finally {
      setIsSimulating(false);
    }
  };

  return {
    currentStepIndex,
    isSimulating,
    handleNextStep,
    totalSteps: simulationSteps.length,
    currentStep: simulationSteps[currentStepIndex],
  };
};
