import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 dark:text-white">404</h1>
        <p className="mt-4 text-xl text-gray-600 dark:text-gray-400">
          페이지를 찾을 수 없습니다.
        </p>
        <p className="mt-2 text-gray-500 dark:text-gray-500">
          요청하신 페이지가 존재하지 않거나 이동되었습니다.
        </p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-md bg-primary px-6 py-3 text-white transition-colors hover:bg-primary/90"
        >
          홈으로 돌아가기
        </Link>
      </div>
    </div>
  );
} 