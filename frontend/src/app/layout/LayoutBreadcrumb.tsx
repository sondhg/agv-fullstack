import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

export function LayoutBreadcrumb() {
  const location = useLocation(); // Get the current location
  const [currentUrl, setCurrentUrl] = useState(window.location.href);

  useEffect(() => {
    // Update the URL whenever location changes
    setCurrentUrl(window.location.href);
  }, [location]);

  const [protocol, rest] = currentUrl.split("//");
  const [host, ...pathParts] = rest.split("/");
  const path = pathParts.join("/");
  const coloredPath = (
    <span className="bg-gradient-to-r from-blue-500 to-green-500 bg-clip-text font-semibold text-transparent">
      {path}
    </span>
  );
  return (
    <div className="flex w-full items-center justify-between">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem className="hidden md:block">
            <BreadcrumbLink href="/">AGV System</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator className="hidden md:block" />
          <BreadcrumbItem>
            <BreadcrumbPage>
              {protocol}//{host}/{coloredPath}
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Search command trigger */}
      <Button
        variant="outline"
        size="sm"
        className="ml-auto flex items-center gap-1"
        onClick={() => {
          // Simulate the keyboard shortcut to open the command menu
          const event = new KeyboardEvent("keydown", {
            key: "k",
            ctrlKey: true,
            bubbles: true,
          });
          document.dispatchEvent(event);
        }}
      >
        <Search className="h-4 w-4" />
        <span className="hidden sm:inline-flex">Search</span>
        <kbd className="pointer-events-none ml-auto hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
          <span className="text-xs">CTRL</span>K
        </kbd>
      </Button>
    </div>
  );
}
