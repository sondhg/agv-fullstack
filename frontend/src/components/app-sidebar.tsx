import { SidebarTriggerWithTooltip } from "@/app/layout/SidebarTriggerWithTooltip";
import { NavMain } from "@/components/nav-main";
import { NavUser } from "@/components/nav-user";
import { TeamSwitcher } from "@/components/team-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { useAuth } from "@/hooks/useAuth";
import { FRONTEND_ROUTES } from "@/routes/routes";
import {
  FlaskConical,
  GalleryThumbnails,
  Navigation,
  PlaneLanding,
  University,
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
          title: FRONTEND_ROUTES.map.title,
          url: FRONTEND_ROUTES.map.path,
          icon: FRONTEND_ROUTES.map.icon,
        },
        {
          title: FRONTEND_ROUTES.agvs.title,
          url: FRONTEND_ROUTES.agvs.path,
          icon: FRONTEND_ROUTES.agvs.icon,
        },
        {
          title: FRONTEND_ROUTES.orders.title,
          url: FRONTEND_ROUTES.orders.path,
          icon: FRONTEND_ROUTES.orders.icon,
        },
        // {
        //   title: FRONTEND_ROUTES.dashboard.title,
        //   url: FRONTEND_ROUTES.dashboard.path,
        //   icon: FRONTEND_ROUTES.dashboard.icon,
        // },
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
          icon: FRONTEND_ROUTES.home.icon,
        },
        {
          title: FRONTEND_ROUTES.login.title,
          url: FRONTEND_ROUTES.login.path,
          icon: FRONTEND_ROUTES.login.icon,
        },
        {
          title: FRONTEND_ROUTES.register.title,
          url: FRONTEND_ROUTES.register.path,
          icon: FRONTEND_ROUTES.register.icon,
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
          icon: FRONTEND_ROUTES.dashboardDemo.icon,
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
        <SidebarTriggerWithTooltip side="right" />
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
