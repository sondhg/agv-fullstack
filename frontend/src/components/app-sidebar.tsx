import { NavMain } from "@/components/nav-main";
import { NavUser } from "@/components/nav-user";
import { TeamSwitcher } from "@/components/team-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { useAuth } from "@/hooks/useAuth";
import {
  Car,
  ChartLine,
  FlaskConical,
  GalleryThumbnails,
  House,
  ListOrdered,
  LogIn,
  Map,
  Navigation,
  PlaneLanding,
  University,
  UserPlus,
} from "lucide-react";

// This is sample data.
const data = {
  teams: [
    {
      name: "iPAC Lab",
      logo: FlaskConical,
      plan: "Company",
    },
    {
      name: "HUST",
      logo: University,
      plan: "University",
    },
  ],
  navMain: [
    {
      title: "Admin",
      url: "#",
      icon: Navigation,
      isActive: true,
      items: [
        {
          title: "Map",
          url: "/admin/map",
          icon: Map,
        },
        {
          title: "AGVs",
          url: "/admin/agvs",
          icon: Car,
        },
        {
          title: "Orders",
          url: "/admin/orders",
          icon: ListOrdered,
        },
        {
          title: "Dashboard",
          url: "/admin/dashboard",
          icon: ChartLine,
        },
      ],
    },
    {
      title: "Home & Auth",
      url: "#",
      icon: PlaneLanding,
      items: [
        {
          title: "Home",
          url: "/home",
          icon: House,
        },
        {
          title: "Login",
          url: "/login",
          icon: LogIn,
        },
        {
          title: "Register",
          url: "/register",
          icon: UserPlus,
        },
      ],
    },
    {
      title: "Demos (for view only)",
      url: "#",
      icon: GalleryThumbnails,
      items: [
        {
          title: "Dashboard Demo",
          url: "/demo/dashboard-demo",
          icon: ChartLine,
        },
      ],
    },
  ],
};

export function AppSidebar({ ...props }) {
  const { account, isAuthenticated } = useAuth();

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <SidebarTrigger className="ml-0.5" />
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      {/* Conditionally render SidebarFooter based on authentication */}
      {isAuthenticated && account && (
        <SidebarFooter>
          <NavUser account={account} />
        </SidebarFooter>
      )}
      <SidebarRail />
    </Sidebar>
  );
}
