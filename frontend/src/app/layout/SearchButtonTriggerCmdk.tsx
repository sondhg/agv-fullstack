import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

export function SearchButtonTriggerCmdk() {
  return (
    <Button
      variant="outline"
      size="sm"
      className="relative h-8 w-full justify-start rounded-[0.5rem] border border-input bg-muted/50 px-4 py-2 text-sm font-normal text-muted-foreground shadow-none hover:bg-accent hover:text-accent-foreground sm:pr-12 md:w-40 lg:w-56 xl:w-64"
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
      <Search />
      <span className="hidden lg:inline-flex">Search pages...</span>
      <span className="inline-flex lg:hidden">Search...</span>
      <kbd className="pointer-events-none absolute right-[0.3rem] top-[0.3rem] hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
        <span className="text-xs">⌘</span>K
      </kbd>
    </Button>
  );
}
