import { useAuth } from "@/hooks/useAuth";
import { AlertHasLoggedIn } from "./AlertHasLoggedIn";
import { AlertNotLoggedIn } from "./AlertNotLoggedIn";
import { HowToUseGUIGuide } from "./HowToUseGUIGuide";

export function HomePage() {
  const { isAuthenticated } = useAuth();
  return (
    <>
      <h2 className="text-3xl font-bold">Home</h2>
      {isAuthenticated ? <AlertHasLoggedIn /> : <AlertNotLoggedIn />}
      <div className="flex items-center justify-center">
        <HowToUseGUIGuide />
      </div>
    </>
  );
}
