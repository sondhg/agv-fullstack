import { useAuth } from "@/hooks/useAuth";
import { AlertHasLoggedIn } from "./sections/AlertHasLoggedIn";
import { AlertNotLoggedIn } from "./sections/AlertNotLoggedIn";
import { HowToUseGUIGuide } from "./sections/HowToUseGUIGuide";

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
