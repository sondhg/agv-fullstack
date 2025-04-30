import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// Define navigation items based on the routes in AllRoutes.tsx
const navigationItems = [
  { title: "Home", path: "/home" },
  { title: "Map", path: "/admin/map" },
  { title: "AGVs", path: "/admin/agvs" },
  { title: "Orders", path: "/admin/orders" },
  { title: "Dashboard", path: "/admin/dashboard" },
  { title: "Login", path: "/login" },
  { title: "Register", path: "/register" },
  { title: "Dashboard Demo", path: "/demo/dashboard-demo" },
];

interface SearchCommandProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function SearchCommand({ open, onOpenChange }: SearchCommandProps) {
  const navigate = useNavigate();

  // Use dialog mode or inline mode based on the isDialog prop
  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Navigate pages">
          {navigationItems.map((item) => (
            <CommandItem
              key={item.path}
              onSelect={() => {
                navigate(item.path);
                onOpenChange?.(false);
              }}
            >
              {item.title}
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}

// Create a component that handles keyboard shortcut and dialog
export function CommandMenu() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  return <SearchCommand open={open} onOpenChange={setOpen} />;
}
