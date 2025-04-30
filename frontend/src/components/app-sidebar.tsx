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
import { ADMIN_AGVS, ADMIN_DASHBOARD, ADMIN_MAP, ADMIN_ORDERS, DEMO_DASHBOARD, HOME, LOGIN, REGISTER } from "@/constants/routes";
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
          url: ADMIN_MAP,
          icon: Map,
        },
        {
          title: "AGVs",
          url: ADMIN_AGVS,
          icon: Car,
        },
        {
          title: "Orders",
          url: ADMIN_ORDERS,
          icon: ListOrdered,
        },
        {
          title: "Dashboard",
          url: ADMIN_DASHBOARD,
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
          url: HOME,
          icon: House,
        },
        {
          title: "Login",
          url: LOGIN,
          icon: LogIn,
        },
        {
          title: "Register",
          url: REGISTER,
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
          url: DEMO_DASHBOARD,
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
