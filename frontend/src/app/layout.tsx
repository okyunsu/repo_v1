import { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/app/globals.css";
import ClientLayout from "@/components/Common/ClientLayout";
import NextAuthSessionProvider from "@/components/Providers/SessionProvier";
import ToastProvider from "@/components/Providers/ToastProvider";
import AuthSessionProvider from "@/components/Providers/AuthSessionProvider";
const inter = Inter({ subsets: ["latin"],display: 'swap'});

export const metadata: Metadata = {
  title: {
    template: '%s | 웹 파이낸셜 대시보드',
    default: '웹 파이낸셜 대시보드',
  },
  description: '기업 재무제표 분석 및 대시보드',
  manifest: '/manifest.json',
  icons: {
    apple: '/icons/icon-192x192.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <NextAuthSessionProvider>
      <AuthSessionProvider>
        <html lang="ko" suppressHydrationWarning>
          <body className={`dark:bg-black ${inter.className}`}>
            <ClientLayout>{children}</ClientLayout>
            <ToastProvider />
          </body>
        </html>
      </AuthSessionProvider>
    </NextAuthSessionProvider>
  );
}

