# 역할: 내 프로필 저장/조회 유스케이스
# - 유저 존재 확인 같은 업무 규칙 포함

class UserService:
    def __init__(self, user_repo, health_repo):
        self.user_repo = user_repo
        self.health_repo = health_repo

    def upsert_my_profile(self, *, user_id: int, profile: dict) -> dict:
        if self.user_repo.get_by_id(user_id) is None:
            raise ValueError("USER_NOT_FOUND")
        return self.health_repo.upsert(user_id, profile)

    def get_my_profile(self, *, user_id: int) -> dict:
        if self.user_repo.get_by_id(user_id) is None:
            raise ValueError("USER_NOT_FOUND")
        return self.health_repo.get_by_user_id(user_id) or {}
