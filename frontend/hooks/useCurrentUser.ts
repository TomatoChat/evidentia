"use client";

import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api_cjs.cjs";

export function useCurrentUser() {
  const user = useQuery(api.users.getCurrentUser);
  
  return {
    user,
    isLoading: user === undefined,
    isAuthenticated: user !== null,
  };
}