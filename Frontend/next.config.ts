import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    reactStrictMode: true,
    eslint: {
          ignoreDuringBuilds: true,
    },
    typescript: {
          ignoreBuildErrors: true,
    },
    async rewrites() {
          return [
                {
                      source: "/api/:path*",
                      destination: "/.netlify/functions/api/:path*",
                },
          ];
    },
};

export default nextConfig;
