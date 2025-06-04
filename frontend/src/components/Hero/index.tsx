"use client";
import Image from "next/image";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export default function Hero() {
  const [email, setEmail] = useState("");
  const router = useRouter();
  const { userId, accessToken } = useAuthStore();
  const isAuthenticated = !!userId && !!accessToken;

  const handleSubmit = (e) => {
    e.preventDefault();
  };

  const handleDashboardClick = (e) => {
    e.preventDefault();
    if (isAuthenticated) {
      router.push('/dashboard');
    } else {
      router.push('/auth/login');
    }
  };

  return (
    <>
      <section className="overflow-hidden pb-20 pt-35 md:pt-40 xl:pb-25 xl:pt-46">
        <div className="mx-auto max-w-c-1390 px-4 md:px-8 2xl:px-0">
          <div className="flex lg:items-center lg:gap-8 xl:gap-32.5">
            <div className=" md:w-1/2">
              <h4 className="mb-4.5 text-lg font-medium text-black dark:text-white">
                🔥 LIF - Life, Intelligence, Future
              </h4>
              <h1 className="mb-5 pr-16 text-3xl font-bold text-black dark:text-white xl:text-hero ">
                금융 서비스 플랫폼 {"   "}
                <span className="relative inline-block before:absolute before:bottom-2.5 before:left-0 before:-z-1 before:h-3 before:w-full before:bg-titlebg dark:before:bg-titlebgdark ">
                  LIF
                </span>
              </h1>
              <p className="mb-6">
                Life, Intelligence, Future - 혁신적인 금융 서비스 플랫폼으로 
                더 나은 금융 생활을 경험하세요. 쉽고 편리한 금융 서비스를 통해 
                당신의 미래를 설계하세요.
              </p>

              <div className="mt-10">
                <a
                  href="#"
                  onClick={handleDashboardClick}
                  className="inline-flex items-center justify-center rounded-md bg-primary px-8 py-3.5 text-base font-medium text-white duration-300 ease-in-out hover:bg-primary/90"
                >
                  {isAuthenticated ? "대시보드 이동하기" : "로그인하고 시작하기"}
                  <svg
                    className="ml-2 h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M14 5l7 7m0 0l-7 7m7-7H3"
                    ></path>
                  </svg>
                </a>
              </div>
            </div>

            <div className="animate_right hidden md:w-1/2 lg:block">
              <div className="relative 2xl:-mr-7.5">
                <Image
                  src="/images/shape/shape-01.png"
                  alt="shape"
                  width={46}
                  height={246}
                  className="absolute -left-11.5 top-0"
                  style={{ height: 'auto' }}
                />
                <Image
                  src="/images/shape/shape-02.svg"
                  alt="shape"
                  width={36.9}
                  height={36.7}
                  className="absolute bottom-0 right-0 z-10"
                  style={{ height: 'auto' }}
                />
                <Image
                  src="/images/shape/shape-03.svg"
                  alt="shape"
                  width={21.64}
                  height={21.66}
                  className="absolute -right-6.5 bottom-0 z-1"
                  style={{ height: 'auto' }}
                />
                <div className=" relative aspect-[700/444] w-full">
                  <Image
                    className="shadow-solid-l dark:hidden"
                    src="/images/hero/hero-light.svg"
                    alt="Hero"
                    fill
                    priority
                  />
                  <Image
                    className="hidden shadow-solid-l dark:block"
                    src="/images/hero/hero-dark.svg"
                    alt="Hero"
                    fill
                    priority
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
