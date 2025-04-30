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
import { FRONTEND_ROUTES } from "@/routes/routes";
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
      title: "Admin pages",
      url: "#",
      icon: Navigation,
      isActive: true,
      items: [
        {
          title: FRONTEND_ROUTES.map.title,
          url: FRONTEND_ROUTES.map.path,
          icon: Map,
        },
        {
          title: FRONTEND_ROUTES.agvs.title,
          url: FRONTEND_ROUTES.agvs.path,
          icon: Car,
        },
        {
          title: FRONTEND_ROUTES.orders.title,
          url: FRONTEND_ROUTES.orders.path,
          icon: ListOrdered,
        },
        {
          title: FRONTEND_ROUTES.dashboard.title,
          url: FRONTEND_ROUTES.dashboard.path,
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
          title: FRONTEND_ROUTES.home.title,
          url: FRONTEND_ROUTES.home.path,
          icon: House,
        },
        {
          title: FRONTEND_ROUTES.login.title,
          url: FRONTEND_ROUTES.login.path,
          icon: LogIn,
        },
        {
          title: FRONTEND_ROUTES.register.title,
          url: FRONTEND_ROUTES.register.path,
          icon: UserPlus,
        },
      ],
    },
    {
      title: "Demos",
      url: "#",
      icon: GalleryThumbnails,
      items: [
        {
          title: FRONTEND_ROUTES.dashboardDemo.title,
          url: FRONTEND_ROUTES.dashboardDemo.path,
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
