import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
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
  );
}
