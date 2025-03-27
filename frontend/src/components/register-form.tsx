// register-form.tsx

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { postRegister } from "@/services/APIs/authAPI"; // Make sure this function is defined
import { useRef, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { toast } from "sonner";

export function RegisterForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const nameRef = useRef<HTMLInputElement | null>(null);
  const emailRef = useRef<HTMLInputElement | null>(null);
  const passwordRef = useRef<HTMLInputElement | null>(null);
  const repeatPasswordRef = useRef<HTMLInputElement | null>(null);
  const navigate = useNavigate();

  const validateEmail = (email: string) => {
    return String(email)
      .toLowerCase()
      .match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
  };

  const handleRegister = async () => {
    if (!name) {
      toast.error("Name cannot be empty");
      nameRef.current?.classList.add("border-red-500");
      return;
    }

    if (!validateEmail(email)) {
      toast.error("Invalid email");
      emailRef.current?.classList.add("border-red-500");
      return;
    }

    if (!password) {
      toast.error("Password cannot be empty");
      passwordRef.current?.classList.add("border-red-500");
      return;
    }

    if (password !== repeatPassword) {
      toast.error("Passwords do not match");
      repeatPasswordRef.current?.classList.add("border-red-500");
      return;
    }

    setIsLoading(true);

    const registerInfo = { email: email.trim(), password, name };

    try {
      const data = await postRegister(registerInfo);
      if (data && data.email) {
        toast.success("Registration successful");
        navigate("/login");
      } else {
        toast.error("Registration failed");
      }
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error("An unknown error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    setState: React.Dispatch<React.SetStateAction<string>>,
    ref: React.RefObject<HTMLInputElement>,
  ) => {
    setState(event.target.value);
    ref.current?.classList.remove("border-red-500");
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleRegister();
    }
  };

  return (
    <Card className="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle className="text-2xl">Register</CardTitle>
        <CardDescription>
          Enter your details to create an account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              type="text"
              placeholder="Your Name"
              value={name}
              onChange={(event) => handleInputChange(event, setName, nameRef)}
              onKeyDown={handleKeyDown}
              onFocus={() =>
                nameRef.current?.classList.remove("border-red-500")
              }
              ref={nameRef}
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              value={email}
              onChange={(event) => handleInputChange(event, setEmail, emailRef)}
              onKeyDown={handleKeyDown}
              onFocus={() =>
                emailRef.current?.classList.remove("border-red-500")
              }
              ref={emailRef}
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(event) =>
                handleInputChange(event, setPassword, passwordRef)
              }
              onKeyDown={handleKeyDown}
              onFocus={() =>
                passwordRef.current?.classList.remove("border-red-500")
              }
              ref={passwordRef}
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="repeat-password">Repeat Password</Label>
            <Input
              id="repeat-password"
              type="password"
              value={repeatPassword}
              onChange={(event) =>
                handleInputChange(event, setRepeatPassword, repeatPasswordRef)
              }
              onKeyDown={handleKeyDown}
              onFocus={() =>
                repeatPasswordRef.current?.classList.remove("border-red-500")
              }
              ref={repeatPasswordRef}
              required
            />
          </div>
          <Button
            type="button"
            onClick={handleRegister}
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? "Registering..." : "Register"}
          </Button>
        </div>
        <div className="mt-4 text-center text-sm">
          Already have an account?{" "}
          <NavLink to="/login" className="underline">
            Login
          </NavLink>
        </div>
        <div className="mt-4 text-center text-sm">
          Or go back to{" "}
          <NavLink to="/home" className="underline">
            Home page
          </NavLink>
        </div>
      </CardContent>
    </Card>
  );
}
