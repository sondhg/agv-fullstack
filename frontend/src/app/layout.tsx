import { AppSidebar } from "@/components/app-sidebar";
import { CommandMenu } from "@/components/search-command";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { Outlet } from "react-router-dom";
import { LayoutHeader } from "./layout/LayoutHeader";

export default function Layout() {
  return (
    <SidebarProvider>
      {/* Add CommandMenu for keyboard shortcut searching */}
      <CommandMenu />
      <AppSidebar />
      <SidebarInset>
        <div
          className="transition-border-radius ease-cubic origin-top transition-transform duration-500"
        >
          <div className="relative flex min-h-svh flex-col bg-background">
            <div data-wrapper className="border-grid flex flex-1 flex-col">
              <LayoutHeader />
              <main className="flex flex-1 flex-col gap-4 p-4">
                <Outlet /> {/* Renders the nested routes */}
              </main>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
