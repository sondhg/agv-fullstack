import { SIMULATION_STEP_KEY } from "@/constants/localStorageKeys.ts";
import { simulateUpdateAgvPosition } from "@/services/APIs/agvsAPI";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { simulationSteps } from "./simulationSteps.ts";

export const useStepSimulation = (onUpdateSuccess?: () => Promise<void>) => {
  // Initialize state from localStorage if available, otherwise start from step 0
  const [currentStepIndex, setCurrentStepIndex] = useState(() => {
    const savedStep = localStorage.getItem(SIMULATION_STEP_KEY);
    return savedStep ? parseInt(savedStep, 10) : 0;
  });
  const [isSimulating, setIsSimulating] = useState(false);

  // Save step index to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(SIMULATION_STEP_KEY, currentStepIndex.toString());
  }, [currentStepIndex]);

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

  // Add a function to reset the simulation
  const resetSimulation = () => {
    setCurrentStepIndex(0);
    localStorage.removeItem(SIMULATION_STEP_KEY);
    toast.info("Simulation has been reset to the beginning");
  };

  return {
    currentStepIndex,
    isSimulating,
    handleNextStep,
    resetSimulation,
    totalSteps: simulationSteps.length,
    currentStep: simulationSteps[currentStepIndex],
  };
};
