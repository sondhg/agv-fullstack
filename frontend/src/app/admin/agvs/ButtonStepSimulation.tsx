import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";
import { useStepSimulation } from "./useStepSimulation";

interface ButtonStepSimulationProps {
  onUpdateSuccess?: () => Promise<void>;
}

export function ButtonStepSimulation({
  onUpdateSuccess,
}: ButtonStepSimulationProps) {
  const {
    currentStepIndex,
    isSimulating,
    handleNextStep,
    totalSteps,
    currentStep,
  } = useStepSimulation(onUpdateSuccess);

  return (
    <Button
      onClick={handleNextStep}
      disabled={isSimulating}
      className="flex items-center space-x-2 rounded-lg bg-opacity-70 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 px-4 py-2 text-white backdrop-blur-md hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 disabled:opacity-50"
    >
      <Play />
      <span>
        {isSimulating
          ? "Simulating..."
          : `Simulate step ${currentStepIndex + 1}/${totalSteps} (AGV ${currentStep.agv_id} → node ${currentStep.current_node})`}
      </span>
    </Button>
  );
}
