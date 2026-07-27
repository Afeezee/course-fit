import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import { AuthWrapper } from "@/components/AuthWrapper";
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
  return (
    <html lang="en" className={`${display.variable} ${sans.variable}`}>
      <body className="relative min-h-dvh">
        <div className="relative z-10">
          <AuthWrapper>{children}</AuthWrapper>
        </div>
      </body>
    </html>
  );
}
