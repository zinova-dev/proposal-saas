import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Proposal SaaS | Manage your commercial proposals",
  description: "A professional tool for freelancers to generate and manage commercial proposals.",
  other: {
    google: "notranslate",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" translate="no">
      <body className="notranslate bg-gray-50 text-gray-900 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
