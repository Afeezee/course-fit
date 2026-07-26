"use client";

import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";
import { AUTH_ENABLED } from "@/lib/clerkFlag";

// Right-side controls in the header of every page.
// - Auth not configured (no keys) → renders nothing; the app is
//   fully usable anonymously.
// - Signed out → subtle "Sign in" pill.
// - Signed in → link to /history + Clerk's avatar/user menu (which
//   provides the sign-out action).
export function AuthHeader() {
  if (!AUTH_ENABLED) return null;
  return (
    <div className="flex items-center gap-3 text-sm">
      <SignedIn>
        <Link
          href="/history"
          className="rounded-full border border-rule px-3 py-1.5 text-ink-muted transition-colors hover:border-ink hover:text-ink"
        >
          History
        </Link>
        <UserButton
          appearance={{
            elements: {
              userButtonAvatarBox: "h-8 w-8 border border-rule",
            },
          }}
        />
      </SignedIn>
      <SignedOut>
        <SignInButton mode="modal">
          <button
            type="button"
            className="rounded-full border border-rule px-3 py-1.5 text-ink-muted transition-colors hover:border-ink hover:text-ink"
          >
            Sign in
          </button>
        </SignInButton>
      </SignedOut>
    </div>
  );
}
