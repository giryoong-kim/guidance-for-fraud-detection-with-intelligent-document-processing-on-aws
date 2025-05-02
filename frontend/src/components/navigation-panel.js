import {
    SideNavigation,
    SideNavigationProps,
  } from "@cloudscape-design/components";
  //import { useNavigationPanelState } from "../common/hooks/use-navigation-panel-state";
  import { useState } from "react";
  //import { useOnFollow } from "../common/hooks/use-on-follow";
  import { APP_NAME } from "../common/constants";
  import { useLocation } from "react-router-dom";
  
  export default function NavigationPanel() {
   // const location = useLocation();
   // const onFollow = useOnFollow();
   // const [navigationPanelState, setNavigationPanelState] =
   //   useNavigationPanelState();
  
    const [items] = useState(() => {
      const items = [
        {
          type: "link",
          text: "Home",
          href: "/",
        },
        {
          type: "section",
          text: "Workflow",
          items: [
            { type: "link", text: "Create", href: "/workflow/create" },
            //{ type: "link", text: "Update", href: "/workflow/update" },
            { type: "link", text: "Review", href: "/workflow/review" },
          ],
        },
      ];

      return items;
    });
  
  
    return (
      <SideNavigation
        header={{ href: "/", text: APP_NAME }}
        items={items.map((value, idx) => {
          return value;
        })}
      />
    );
  }