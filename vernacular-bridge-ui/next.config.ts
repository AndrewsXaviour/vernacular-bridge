import type { NextConfig } from "next";

/**
 * Next.js configuration with dynamic backend URL via environment variable.
 * Falls back to localhost:8000 for local development.
 * In production (Vercel), set NEXT_PUBLIC_API_URL to the Railway/Cloud Run backend URL.
 */
const nextConfig: NextConfig = {
  async rewrites() {
    const backendUrl = process.env.API_URL || "http://127.0.0.1:8000";

    return [
      {
        source: "/api/full-flow",
        destination: `${backendUrl}/full-flow`,
      },
      {
        source: "/api/coach",
        destination: `${backendUrl}/coach`,
      },
      {
        source: "/api/navigator/:path*",
        destination: `${backendUrl}/navigator/:path*`,
      },
      {
        source: "/api/learn",
        destination: `${backendUrl}/learn`,
      },
      {
        source: "/api/generate",
        destination: `${backendUrl}/generate`,
      },
      {
        source: "/api/entitlements",
        destination: `${backendUrl}/entitlements`,
      },
      {
        source: "/api/processes",
        destination: `${backendUrl}/processes`,
      },
      {
        source: "/api/health",
        destination: `${backendUrl}/health`,
      },
    ];
  },
};

export default nextConfig;
