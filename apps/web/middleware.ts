import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse, type NextRequest } from "next/server";

const isProtected = createRouteMatcher(["/history(.*)"]);

// clerkMiddleware() itself throws when instantiated without a Clerk
// secret key, so we only construct it when auth is actually
// configured. Without keys, every request passes through — the
// /history route is just unreachable via the nav.
const HAS_CLERK =
  Boolean(process.env.CLERK_SECRET_KEY) &&
  Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

const activeMiddleware = HAS_CLERK
  ? clerkMiddleware((auth, req) => {
      if (isProtected(req)) auth().protect();
    })
  : (_req: NextRequest) => NextResponse.next();

export default activeMiddleware;

export const config = {
  matcher: [
    "/((?!_next|.*\\..*).*)",
    "/",
  ],
};
