import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Raíz siempre = carpeta frontend (donde está next.config), así el resolver usa frontend/node_modules
  turbopack: {
    root: path.resolve(__dirname),
  },
  reactStrictMode: true,
  // Asegura que webpack resuelva módulos desde frontend/node_modules (evita resolver en proyecto raíz o home)
  webpack: (config) => {
    config.resolve = config.resolve ?? {};
    config.resolve.modules = [
      path.join(__dirname, "node_modules"),
      ...(Array.isArray(config.resolve.modules) ? config.resolve.modules : ["node_modules"]),
    ];
    return config;
  },
};

export default nextConfig;
