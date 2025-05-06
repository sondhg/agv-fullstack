import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { forwardRef } from "react";
import { useStepSimulation } from "./useStepSimulation";
interface ButtonStepSimulationProps {
  onUpdateSuccess?: () => Promise<void>;
  onResetRef?: (resetFn: () => void) => void;
}

/**
 * Button component that handles step-by-step AGV simulation
 *
 * @param props.onUpdateSuccess - Callback function to run after successful position update
 * @param props.onResetRef - Function to provide the reset functionality to parent components
 * @param ref - Forwarded ref to allow programmatic triggering of the button (e.g., via keyboard shortcuts)
 */
export const ButtonStepSimulation = forwardRef<
  HTMLButtonElement,
  ButtonStepSimulationProps
>(function ButtonStepSimulation({ onUpdateSuccess, onResetRef }, ref) {
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
    <Button
      onClick={handleNextStep}
      disabled={isSimulating}
      className="h-full min-w-[180px] p-2"
      ref={ref}
    >
      {isSimulating ? (
        <span className="text-sm font-medium">Simulating...</span>
      ) : (
        <div className="flex flex-col space-y-1">
          <span className="text-sm font-semibold">Auto Simulate</span>
          <Badge variant={"secondary"}>
            <span>Click or press &nbsp;</span>
            <span>
              <kbd>Alt + S</kbd>
            </span>
          </Badge>
          <div className="space-y-0.5">
            <div>
              Step <span className="font-medium">{currentStepIndex + 1}</span>/
              {totalSteps}
            </div>
            <div>
              AGV {currentStep.agv_id} → {currentStep.current_node}
            </div>
          </div>
        </div>
      )}
    </Button>
  );
});
