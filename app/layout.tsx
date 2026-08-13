import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Northstar | Merchandise Planning & Assortment Optimization",
  description: "A multi-store retail merchandising analytics and inventory planning system by Chelaka Fernando.",
  keywords: ["merchandise planning", "retail analytics", "assortment optimization", "inventory planning", "portfolio"],
  authors: [{ name: "Chelaka Fernando" }],
  openGraph: {
    title: "Northstar Merchandise Intelligence",
    description: "A complete merchandise planning and analytics system for a 10-store Canadian retail network.",
    type: "website",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
