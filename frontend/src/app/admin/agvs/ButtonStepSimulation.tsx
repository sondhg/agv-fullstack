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
      className="h-full"
      ref={ref} // Forward the ref to the Button component
    >
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
});
