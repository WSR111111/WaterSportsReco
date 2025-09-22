import { useEffect, useState } from "react";

// 카카오맵 SDK 동적 로더 (도메인 허용등록 필수)
export default function useKakaoLoader(appkey, { timeoutMs = 8000 } = {}) {
  const [state, setState] = useState({ loaded: false, error: null });

  useEffect(() => {
    if (!appkey) {
      setState({ loaded: false, error: new Error("카카오맵 API 키가 설정되지 않았습니다") });
      return;
    }

    if (window.kakao && window.kakao.maps) {
      setState({ loaded: true, error: null });
      return;
    }

    // 중복 삽입 방지
    let script = document.querySelector('script[data-kakao-sdk="true"]');
    const onScriptLoad = () => {
      if (window.kakao && window.kakao.maps) {
        window.kakao.maps.load(() => setState({ loaded: true, error: null }));
      } else {
        setState({ loaded: false, error: new Error("Kakao SDK 로드됨, maps API 없음") });
      }
    };
    const onScriptError = () => setState({ loaded: false, error: new Error("Kakao SDK 로드 실패") });

    if (!script) {
      script = document.createElement("script");
      script.setAttribute("data-kakao-sdk", "true");
      script.async = true;
      script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${appkey}&autoload=false`;
      script.onload = onScriptLoad;
      script.onerror = onScriptError;
      document.head.appendChild(script);
    } else if (script && (window.kakao && window.kakao.maps)) {
      window.kakao.maps.load(() => setState({ loaded: true, error: null }));
    } else {
      script.addEventListener("load", onScriptLoad, { once: true });
      script.addEventListener("error", onScriptError, { once: true });
    }

    const timer = setTimeout(() => {
      if (!(window.kakao && window.kakao.maps)) {
        setState({ loaded: false, error: new Error("Kakao SDK 로드 지연(타임아웃)") });
      }
    }, timeoutMs);

    return () => clearTimeout(timer);
  }, [appkey, timeoutMs]);

  return state;
}
