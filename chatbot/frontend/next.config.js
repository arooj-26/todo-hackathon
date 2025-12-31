/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Enable SWC minification for better performance
  swcMinify: true,

  // Enable standalone output for Docker deployment
  output: 'standalone',

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_OPENAI_DOMAIN_KEY: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY,
    NEXT_PUBLIC_DEFAULT_USER_ID: process.env.NEXT_PUBLIC_DEFAULT_USER_ID,
    NEXT_PUBLIC_USE_CHATKIT: process.env.NEXT_PUBLIC_USE_CHATKIT,
  },

  // Optimize for production
  webpack: (config, { isServer }) => {
    // Fixes npm packages that depend on node modules
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },

  // Enable experimental features for better ChatKit integration
  experimental: {
    optimizePackageImports: ['@openai/chatkit'],
  },
};

module.exports = nextConfig;
