"use client";

import { ClerkProvider } from "@clerk/clerk-react";
import type { ReactNode } from "react";
import { AUTH_ENABLED } from "@/lib/clerkFlag";

// @clerk/clerk-react's ClerkProvider is a client-only component and
// wants publishableKey as an explicit prop (unlike @clerk/nextjs which
// autowires it from env). We had to switch to @clerk/clerk-react
// because @clerk/nextjs ships server actions, which Next.js refuses
// to include in a static export.
//
// When AUTH_ENABLED is false (no publishable key set), skip mounting
// ClerkProvider entirely — the rest of the app works anonymously.
export function AuthWrapper({ children }: { children: ReactNode }) {
  if (!AUTH_ENABLED) return <>{children}</>;
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!}
      appearance={{
        variables: {
          colorPrimary: "#0e1b2c",
          colorText: "#0e1b2c",
          colorBackground: "#f7f5ee",
          fontFamily: "var(--font-sans)",
          borderRadius: "0.5rem",
        },
      }}
    >
      {children}
    </ClerkProvider>
  );
}
