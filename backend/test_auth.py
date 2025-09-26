"""
인증 시스템 테스트 스크립트
"""

import requests
import json
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# API 기본 URL
BASE_URL = "http://localhost:8000/api"

def test_auth_system():
    """인증 시스템 전체 테스트"""
    
    print("🧪 인증 시스템 테스트 시작")
    print("=" * 50)
    
    # 테스트 데이터
    test_user = {
        "email": "test@example.com",
        "password": "Test123!@#",
        "name": "테스트 사용자"
    }
    
    try:
        # 1. 회원가입 테스트
        print("\n1️⃣ 회원가입 테스트")
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_user
        )
        
        if register_response.status_code == 201:
            print("✅ 회원가입 성공")
            print(f"응답: {register_response.json()}")
        else:
            print(f"❌ 회원가입 실패: {register_response.status_code}")
            print(f"에러: {register_response.text}")
            return
        
        # 2. 로그인 테스트
        print("\n2️⃣ 로그인 테스트")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        
        if login_response.status_code == 200:
            print("✅ 로그인 성공")
            tokens = login_response.json()
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
            print(f"Access Token: {access_token[:50]}...")
            print(f"Refresh Token: {refresh_token[:50]}...")
        else:
            print(f"❌ 로그인 실패: {login_response.status_code}")
            print(f"에러: {login_response.text}")
            return
        
        # 3. 사용자 정보 조회 테스트
        print("\n3️⃣ 사용자 정보 조회 테스트")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        me_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers
        )
        
        if me_response.status_code == 200:
            print("✅ 사용자 정보 조회 성공")
            user_info = me_response.json()
            print(f"사용자 정보: {user_info}")
        else:
            print(f"❌ 사용자 정보 조회 실패: {me_response.status_code}")
            print(f"에러: {me_response.text}")
        
        # 4. 토큰 갱신 테스트
        print("\n4️⃣ 토큰 갱신 테스트")
        refresh_response = requests.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        if refresh_response.status_code == 200:
            print("✅ 토큰 갱신 성공")
            new_tokens = refresh_response.json()
            new_access_token = new_tokens["access_token"]
            print(f"새 Access Token: {new_access_token[:50]}...")
        else:
            print(f"❌ 토큰 갱신 실패: {refresh_response.status_code}")
            print(f"에러: {refresh_response.text}")
        
        # 5. 회원정보 수정 테스트
        print("\n5️⃣ 회원정보 수정 테스트")
        update_response = requests.put(
            f"{BASE_URL}/auth/profile",
            headers=headers,
            json={
                "name": "수정된 이름",
                "current_password": test_user["password"]
            }
        )
        
        if update_response.status_code == 200:
            print("✅ 회원정보 수정 성공")
            print(f"응답: {update_response.json()}")
        else:
            print(f"❌ 회원정보 수정 실패: {update_response.status_code}")
            print(f"에러: {update_response.text}")
        
        # 6. 계정 삭제 테스트
        print("\n6️⃣ 계정 삭제 테스트")
        delete_response = requests.delete(
            f"{BASE_URL}/auth/account",
            headers=headers,
            json={"password": test_user["password"]}
        )
        
        if delete_response.status_code == 200:
            print("✅ 계정 삭제 성공")
            print(f"응답: {delete_response.json()}")
        else:
            print(f"❌ 계정 삭제 실패: {delete_response.status_code}")
            print(f"에러: {delete_response.text}")
        
        print("\n🎉 모든 테스트 완료!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

def test_system_info():
    """시스템 정보 테스트"""
    
    print("\n📋 시스템 정보 조회")
    try:
        info_response = requests.get(f"{BASE_URL}/auth/info")
        
        if info_response.status_code == 200:
            print("✅ 시스템 정보 조회 성공")
            info = info_response.json()
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 시스템 정보 조회 실패: {info_response.status_code}")
    
    except Exception as e:
        print(f"❌ 시스템 정보 조회 중 오류: {e}")

if __name__ == "__main__":
    # 시스템 정보 먼저 확인
    test_system_info()
    
    # 전체 인증 시스템 테스트
    test_auth_system()