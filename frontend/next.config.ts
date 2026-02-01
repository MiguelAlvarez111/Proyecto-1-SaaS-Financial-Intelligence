import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Explicit root so Turbopack resolves from frontend/ (fixes Railway and multi-lockfile warning)
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
