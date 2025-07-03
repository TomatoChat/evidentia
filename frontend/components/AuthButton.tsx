"use client";

import { useAuthActions } from "@convex-dev/auth/react";
import { useCurrentUser } from "../hooks/useCurrentUser";
import { Button } from "./ui/Button";
import { UserMenu } from "./UserMenu";
import { convex } from "../lib/convex";

export function AuthButton() {
  // If Convex is not configured, show a simple login button
  if (!convex) {
    return (
      <div className="flex items-center gap-2">
        <Button
          onClick={() => alert("Authentication requires Convex configuration")}
          variant="ghost"
          size="sm"
          className="text-gray-300 hover:text-white hover:bg-gray-800"
        >
          Sign In
        </Button>
      </div>
    );
  }

  const { signIn } = useAuthActions();
  const { user, isLoading } = useCurrentUser();

  if (isLoading) {
    return (
      <div className="w-8 h-8 bg-gray-700 rounded-full animate-pulse" />
    );
  }

  if (user) {
    return <UserMenu user={user} />;
  }

  return (
    <div className="flex items-center gap-2">
      <Button
        onClick={() => signIn("github")}
        variant="ghost"
        size="sm"
        className="text-gray-300 hover:text-white hover:bg-gray-800"
      >
        Sign in with GitHub
      </Button>
      <Button
        onClick={() => signIn("google")}
        variant="ghost"
        size="sm"
        className="text-gray-300 hover:text-white hover:bg-gray-800"
      >
        Sign in with Google
      </Button>
    </div>
  );
}