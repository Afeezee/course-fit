/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Static HTML export — the whole app builds to apps/web/out/ and is
  // served by FastAPI at the root path. This lets one Railway service
  // ship both the frontend and the API in a single container.
  output: "export",
  // trailingSlash: true makes routes emit as /wizard/index.html rather
  // than /wizard.html, so directory-style URLs served by FastAPI
  // StaticFiles(html=True) resolve without a fallback rewrite.
  trailingSlash: true,
  images: { unoptimized: true },
};
export default nextConfig;
