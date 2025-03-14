import { ModeToggle } from "@/components/mode-toggle";
import { RegisterForm } from "@/components/register-form";

export function RegisterPage() {
  return (
    <div className="flex h-screen flex-col items-center justify-center space-y-3">
      <ModeToggle />
      <div className="flex w-full items-center justify-center px-4">
        <RegisterForm />
      </div>
    </div>
  );
}
