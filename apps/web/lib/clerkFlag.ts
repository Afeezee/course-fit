// Single source of truth for "is Clerk auth configured for this build?"
// The NEXT_PUBLIC_ prefix means Next inlines this at build time so
// both server + client code get the same answer.
export const AUTH_ENABLED = Boolean(
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
);
