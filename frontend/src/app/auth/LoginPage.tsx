import { LoginForm } from "@/components/login-form";
import { ModeToggle } from "@/components/mode-toggle";

export function LoginPage() {
  return (
    <div className="flex h-screen flex-col items-center justify-center space-y-3">
      <ModeToggle />
      <div className="flex w-full items-center justify-center px-4">
        <LoginForm />
      </div>
    </div>
  );
}
