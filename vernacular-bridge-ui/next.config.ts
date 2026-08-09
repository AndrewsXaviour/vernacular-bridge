import type { NextConfig } from "next";

/**
 * Next.js configuration with dynamic backend URL via environment variable.
 * Falls back to localhost:8000 for local development.
 * In production (Vercel), set NEXT_PUBLIC_API_URL to the Railway/Cloud Run backend URL.
 */
const nextConfig: NextConfig = {
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

    return [
      {
        source: "/full-flow",
        destination: `${backendUrl}/full-flow`,
      },
      {
        source: "/coach",
        destination: `${backendUrl}/coach`,
      },
      {
        source: "/navigator/:path*",
        destination: `${backendUrl}/navigator/:path*`,
      },
      {
        source: "/learn",
        destination: `${backendUrl}/learn`,
      },
      {
        source: "/generate",
        destination: `${backendUrl}/generate`,
      },
      {
        source: "/entitlements",
        destination: `${backendUrl}/entitlements`,
      },
      {
        source: "/processes",
        destination: `${backendUrl}/processes`,
      },
      {
        source: "/health",
        destination: `${backendUrl}/health`,
      },
    ];
  },
};

export default nextConfig;
