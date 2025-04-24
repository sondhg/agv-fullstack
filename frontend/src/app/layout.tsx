import { AppSidebar } from "@/components/app-sidebar";
import { ModeToggle } from "@/components/mode-toggle";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Outlet } from "react-router-dom";
import { LayoutBreadcrumb } from "./layout/LayoutBreadcrumb";
import { DialogMap } from "./layout/DialogMap";

export default function Layout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 bg-white drop-shadow-sm transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12 dark:bg-black">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger />
            <Separator orientation="vertical" className="h-4" />
            <ModeToggle />
            <Separator orientation="vertical" className="h-4" />
            <DialogMap /> {/* No need to pass mapData */}
            <LayoutBreadcrumb />
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4">
          <Outlet /> {/* Renders the nested routes */}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
