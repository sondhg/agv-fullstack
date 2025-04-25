import { Button } from "@/components/ui/button";
import { useStepSimulation } from "./useStepSimulation";

interface ButtonStepSimulationProps {
  onUpdateSuccess?: () => Promise<void>;
  onResetRef?: (resetFn: () => void) => void;
}

export function ButtonStepSimulation({
  onUpdateSuccess,
  onResetRef,
}: ButtonStepSimulationProps) {
  const {
    currentStepIndex,
    isSimulating,
    handleNextStep,
    resetSimulation,
    totalSteps,
    currentStep,
  } = useStepSimulation(onUpdateSuccess);

  // Pass the reset function to the parent component if the ref is provided
  if (onResetRef) {
    onResetRef(resetSimulation);
  }

  return (
    <Button onClick={handleNextStep} disabled={isSimulating} className="h-full">
      <span>
        {isSimulating ? (
          "Simulating..."
        ) : (
          <div className="flex flex-col">
            <span>Auto Simulate</span>
            <span>
              Step {currentStepIndex + 1}/{totalSteps}
            </span>
            <span>
              (AGV {currentStep.agv_id} → node {currentStep.current_node})
            </span>
          </div>
        )}
      </span>
    </Button>
  );
}
