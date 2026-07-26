import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { AUTH_ENABLED } from "@/lib/clerkFlag";
import "./globals.css";

const display = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
  axes: ["opsz", "SOFT"],
});

const sans = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "CourseFit — JAMB course recommender",
  description:
    "A calm, evidence-based recommender for Nigerian UTME candidates. Checks real JAMB eligibility rules first, then ranks what you qualify for.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // ClerkProvider hard-throws when no publishable key is present, so
  // only mount it when auth is actually configured. The rest of the
  // app (landing + wizard + activity feed) works fine anonymously.
  const body = (
    <html lang="en" className={`${display.variable} ${sans.variable}`}>
      <body className="relative min-h-dvh">
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );

  if (!AUTH_ENABLED) return body;

  return (
    <ClerkProvider
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
      {body}
    </ClerkProvider>
  );
}
