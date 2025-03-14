import { RocketIcon } from "@radix-ui/react-icons";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { NavLink } from "react-router-dom";

const loginText = (
  <span className="text-blue-500 hover:underline">
    <NavLink to={"/login"}>login</NavLink>
  </span>
);
export function AlertNotLoggedIn() {
  return (
    <Alert variant="destructive">
      <RocketIcon className="h-4 w-4" />
      <AlertTitle>IMPORTANT!</AlertTitle>
      <AlertDescription>
        You MUST {loginText} before doing anything else.
      </AlertDescription>
    </Alert>
  );
}
