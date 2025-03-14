import { useAuth } from "@/hooks/useAuth";
import { AlertHasLoggedIn } from "./sections/AlertHasLoggedIn";
import { AlertNotLoggedIn } from "./sections/AlertNotLoggedIn";
import { HomeAbout } from "./sections/HomeAbout";
import { HomeServices } from "./sections/HomeServices";

export function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <h2 className="text-3xl font-bold">Home</h2>
      {isAuthenticated ? <AlertHasLoggedIn /> : <AlertNotLoggedIn />}
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        <HomeAbout />
        <HomeServices />
      </div>
    </>
  );
}
