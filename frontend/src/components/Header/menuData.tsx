import { Menu } from "@/types/menu"

const menuData: Menu[] = [
  {
    id: 1,
    title: "Home",
    newTab: false,
    path: "/",
  },
  {
    id: 2,
    title: "Dashboard",
    newTab: false,
    path: "/dashboard",
  },
  {
    id: 3,
    title: "Profile",
    newTab: false,
    path: "/profile",
  },
  {
    id: 4,
    title: "Login",
    newTab: false,
    path: "/auth/login",
  },
];

export default menuData;
