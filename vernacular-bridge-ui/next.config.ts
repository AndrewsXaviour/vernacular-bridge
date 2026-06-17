import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/full-flow",
        destination: "http://127.0.0.1:8000/full-flow",
      },
      {
        source: "/coach",
        destination: "http://127.0.0.1:8000/coach",
      },
      {
        source: "/navigator",
        destination: "http://127.0.0.1:8000/navigator",
      },
      {
        source: "/learn",
        destination: "http://127.0.0.1:8000/learn",
      },
      {
        source: "/generate",
        destination: "http://127.0.0.1:8000/generate",
      },
    ];
  },
};

export default nextConfig;
