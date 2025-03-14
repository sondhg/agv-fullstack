import { NavMain } from "@/components/nav-main";
import { NavSettings } from "@/components/nav-settings";
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
  CalendarDays,
  Car,
  ChartLine,
  FlaskConical,
  GalleryThumbnails,
  House,
  ListOrdered,
  LogIn,
  Navigation,
  PlaneLanding,
  Settings,
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
      title: "ADMIN pages",
      url: "#",
      icon: Navigation,
      isActive: true,
      items: [
        {
          title: "Dashboard",
          url: "/admin/dashboard",
          icon: ChartLine,
        },
        {
          title: "Orders",
          url: "/admin/orders",
          icon: ListOrdered,
        },
        {
          title: "Schedules",
          url: "/admin/schedules",
          icon: CalendarDays,
        },
        {
          title: "AGVs",
          url: "/admin/agvs",
          icon: Car,
        },
      ],
    },
    {
      title: "Landing pages",
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
      title: "Demo pages",
      url: "#",
      icon: GalleryThumbnails,
      items: [
        {
          title: "Dashboard Demo",
          url: "/demo/dashboard-demo",
          icon: ChartLine,
        },
        {
          title: "Schedules Demo",
          url: "/demo/schedules-demo",
          icon: CalendarDays,
        },
      ],
    },
  ],
  settings: [
    {
      name: "Change theme",
      // url: "#",
      icon: Settings,
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
        <NavSettings settings={data.settings} />
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
