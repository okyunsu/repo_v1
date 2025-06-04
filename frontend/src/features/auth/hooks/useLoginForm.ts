import { useState, FormEvent, ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { signIn } from 'next-auth/react';
import { useUserStore } from '@/store/userStore';
import { setAccessToken } from '@/lib/api/authToken';

interface LoginFormState { 
  id: string;
  password: string;
  error: string;
  success: string;
  isLoading: boolean;
}

export const useLoginForm = () => { 
  const router = useRouter();
  const signin = useAuthStore(state => state.signin);
  
  // 객체 반환 대신 직접 함수 선택 (메모이제이션 문제 해결)
  const setUserId = useUserStore(state => state.setUserId);
  
  const [formState, setFormState] = useState<LoginFormState>({ 
    id: '', 
    password: '', 
    error: '',
    success: '',
    isLoading: false
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => { 
    const { name, value } = e.target;
    setFormState(prev => ({ ...prev, [name]: value }));
  };

  const handleLogin = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!formState.id || !formState.password) {
      setFormState(prev => ({ 
        ...prev, 
        error: '아이디와 비밀번호를 모두 입력해주세요.' 
      }));
      return;
    }

    console.log(`로그인 시도: ${formState.id}, ${formState.password}`);

    try {
      setFormState(prev => ({ ...prev, isLoading: true, error: '' }));
      
      // NextAuth의 Credentials Provider로 로그인 시도
      const result = await signIn('credentials', {
        redirect: false,
        email: formState.id,
        password: formState.password,
        callbackUrl: '/'
      });
      
      console.log('NextAuth 로그인 결과:', result);
      
      if (result?.error) {
        throw new Error(result.error);
      }
      
      if (result?.ok) {
        // 로그인 성공 시 상태 업데이트
        setFormState(prev => ({
          ...prev,
          success: '로그인에 성공했습니다.',
          isLoading: false
        }));
        
        // 사용자 ID 설정 (zustand 스토어 활용)
        setUserId(formState.id);
        
        // NextAuth가 자동으로 세션을 설정하므로, 추가 처리 없이 홈으로 이동
        // useAuthRedirect 훅이 역할에 맞는 페이지로 리다이렉션
        console.log('NextAuth 로그인 성공: 홈으로 이동');
        router.push('/');
      }
    } catch (error) {
      console.error('로그인 오류:', error);
      
      // 에러 메시지 표시
      const errorMessage = error instanceof Error 
        ? error.message 
        : '로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.';
      
      setFormState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false
      }));
    }
  };

  return {
    formState,
    handleChange,
    handleLogin
  };
};

