"""
dependencies.py

현재는 개발 편의를 위해 fake current user(user_id=1)를 반환한다.

JWT 인증으로 교체하는 방법:
1. python-jose, passlib 패키지 사용
2. get_current_user 함수를 아래처럼 교체:

    from fastapi.security import OAuth2PasswordBearer
    from jose import JWTError, jwt

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

    def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: int = int(payload.get("sub"))
        except (JWTError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

3. 이 파일의 get_current_user만 교체하면 모든 라우터에 자동 적용됨.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User


def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Phase 0: fake user (user_id=1) 반환.
    Phase 1에서 JWT Depends로 교체한다.
    """
    user = db.get(User, 1)
    if not user:
        # seed 실행 전이라면 임시 객체 반환 (DB 저장 X)
        return User(id=1, email="dev@jobpilot.kr", nickname="개발자")
    return user
