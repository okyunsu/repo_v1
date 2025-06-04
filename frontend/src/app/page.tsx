import { Metadata } from "next";
import Hero from "@/components/Hero";

export const metadata: Metadata = {
  title: "LIF - Life, Intelligence, Future",

  // other metadata
  description: "Life, Intelligence, Future - 금융 서비스 플랫폼"
};

export default function Home() {
  return (
    <main>
      <Hero />
      {/* <Features /> */}
    </main>
  );
}