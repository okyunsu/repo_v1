const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development'
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
  eslint: {
    // ESLint 에러가 있어도 빌드를 계속 진행
    ignoreDuringBuilds: true,
  },
  typescript: {
    // TypeScript 에러가 있어도 빌드를 계속 진행
    ignoreBuildErrors: true,
  },
  // 환경 변수 설정
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:30080',
  },
};

module.exports = withPWA(nextConfig); 