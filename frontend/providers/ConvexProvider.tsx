"use client";

import { ConvexProvider as BaseConvexProvider } from "convex/react";
import { ConvexAuthProvider } from "@convex-dev/auth/react";
import { ReactNode } from "react";
import { convex } from "../lib/convex";

interface ConvexProviderProps {
  children: ReactNode;
}

export function ConvexProvider({ children }: ConvexProviderProps) {
  if (!convex) {
    // If Convex is not configured, just render children without provider
    return <>{children}</>;
  }

  return (
    <BaseConvexProvider client={convex}>
      <ConvexAuthProvider client={convex}>{children}</ConvexAuthProvider>
    </BaseConvexProvider>
  );
}