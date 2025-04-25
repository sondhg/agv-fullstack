import { Button } from "@/components/ui/button";
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
