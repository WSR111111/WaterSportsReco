# expTest.py
import jwt
import datetime

# 테스트할 토큰 (access_token 또는 refresh_token 넣기)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZW1haWwiOiJldW5qZW9uZzA5MTFAbmF2ZXIuY29tIiwibmFtZSI6Ilx1YjBlNVx1YjBlNSIsImV4cCI6MTc1ODg3MTU5NiwiaWF0IjoxNzU4ODcwNjk2LCJ0eXBlIjoiYWNjZXNzIn0.yVnAfikP16eeYowZQf5bbaWnTrtjIbAOinbJRaGTjr0"

# 서명 검증은 생략 (options={"verify_signature": False})
decoded = jwt.decode(token, options={"verify_signature": False})

# exp / iat를 datetime으로 변환
exp = datetime.datetime.fromtimestamp(decoded["exp"])
iat = datetime.datetime.fromtimestamp(decoded["iat"])

# 사람이 읽기 좋은 결과 출력
print("==== 토큰 디코드 결과 ====")
print(f"유저 ID (sub): {decoded.get('sub')}")
print(f"이메일: {decoded.get('email')}")
print(f"이름: {decoded.get('name')}")
print(f"토큰 종류: {decoded.get('type')}")
print(f"발급 시각 (iat): {iat}")
print(f"만료 시각 (exp): {exp}")
