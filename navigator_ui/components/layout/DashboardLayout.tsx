"use client";

import React from "react";
import { DashboardLayoutProps } from "@/types";

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-[#0a0e1a]">
      {children}
    </div>
  );
}

// Made with Bob
