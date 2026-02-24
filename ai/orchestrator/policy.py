class RouterLogic:
    def __init__(self):
        #
        pass

    def run(self, state: dict) -> str:
        print("\n⚙️ [Orch-Agent] 규칙 기반 경로 판단 중...")

        # 1. 데이터 추출
        # chat_agent에서 설정된 분석 결과 추출
        any_exceed = state.get("any_exceed", False)
        any_allergen = state.get("any_allergen", False)

        # 체크할 플래그 리스트
        flag_keys = ["diabetes_flag", "hypertension_flag", "kidneydisease_flag", "allergy_flag"]

        # 플래그 값 추출 (바로 state에서 꺼냄)
        flags = [state.get(key) for key in flag_keys]

        # --- [조건분기 시작] ---

        # 규칙 1: 필수 플래그 중 하나라도 누락(None)된 경우
        if any(f is None for f in flags):
            reason = "필수 건강 정보(Flags) 일부 누락"
            return self._log_and_return("user_agent", reason)

        # 규칙 2: WARN 판정 - any_exceed 또는 any_allergen이 true인 경우
        # chat_agent가 실행되고 피드백 루프로 돌아왔을 때 이 조건이 활성화됨
        if any_exceed or any_allergen:
            reason = f"위험 성분 감지 (영양성분 초과: {any_exceed}, 알러지: {any_allergen})"
            return self._log_and_return("reco_agent", reason)

        # 규칙 3: 플래그가 모두 존재할 때 합계 계산
        # 0과 1로 구성되어 있다고 가정 (True/False여도 sum 가능)
        flag_sum = sum(int(f) for f in flags)

        if flag_sum >= 1:
            return self._log_and_return("chat_agent", f"질환/알러지 보유 ({flag_sum}단계)")
        else:
            return self._log_and_return("end", "질환/알러지 없음 (정상)")

    def _log_and_return(self, next_step, reason):
        print(f"👉 판단 결과: {next_step} (이유: {reason})")
        return next_step