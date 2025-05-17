import { RocketIcon } from "@radix-ui/react-icons";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function AlertHasLoggedIn() {
  return (
    <Alert variant="default">
      <RocketIcon className="h-4 w-4" />
      <AlertTitle>You are logged in!</AlertTitle>
      <AlertDescription>
        You can logout by clicking the user info footer of the sidebar on the
        left.
      </AlertDescription>
    </Alert>
  );
}
