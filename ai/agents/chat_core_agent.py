#JSON 출력형 - 파싱수정 및 any~등 디테일 보완
import json

class EvidenceGeneration:
    def __init__(self, model, tokenizer, final_profiles=None, products=None):
        self.llm = model # For LangChain compatibility if needed, though not used in generate_prompt current logic
        self.model = model
        self.tokenizer = tokenizer
        # 데이터를 클래스 속성으로 저장
        self.final_profiles = final_profiles if final_profiles is not None else {}
        self.products = products if products is not None else {}

# 1. 당뇨, 고혈압, 신부전 분석
    def evaluate_threshold(self, final_profile_key, product_key) -> overallState:
        """
        영양성분 임계값 초과 여부를 분석하여 overallState 형식으로 반환합니다.
        """
        profile = self.final_profiles.get(str(final_profile_key), {})
        product = self.products.get(str(product_key), {})
'''
        # 디버깅: 데이터 확인
        print(f"\n=== 디버깅 정보 ===")
        print(f"final_profile_key: {final_profile_key} (type: {type(final_profile_key)})")
        print(f"product_key: {product_key} (type: {type(product_key)})")
        print(f"profile 데이터: {profile}")
        print(f"product 데이터: {product}")
        print(f"self.final_profiles의 키들: {list(self.final_profiles.keys())}")
        print(f"self.products의 키들: {list(self.products.keys())}")
'''
        # 1. overallState 구조에 맞게 결과 객체 초기화
        state: overallState = {
            "any_exceed": False,
            "exceeded_nutrients": []
        }

        # 2. 분석 제외 키 설정
        exclude_keys = ['user_id', 'restricted_ingredients']
        target_nutrients = [k for k in profile.keys() if k not in exclude_keys]
        
        print(f"target_nutrients (분석 대상): {target_nutrients}")

        # 3. 영양성분 전수 조사
        for nutrient in target_nutrients:
            limit = profile[nutrient]
            
            # 컬럼 이름이 동일하므로 그대로 사용 (fat_ratio만 예외)
            actual = product.get(nutrient, 0)
            
            #print(f"\n[체크] {nutrient}: 기준={limit}, 실제={actual}")

            # fat_ratio는 비율 계산 필요 (지방 칼로리 / 총 칼로리)
            if nutrient == 'fat_ratio':
                total_calories = product.get('calories', 0)
                fat_calories = product.get('fat', 0) * 9  # 지방 1g = 9kcal
                if total_calories > 0:
                    actual_ratio = fat_calories / total_calories
                    #print(f"  지방 비율 계산: {fat_calories}kcal / {total_calories}kcal = {actual_ratio:.3f}")
                    if actual_ratio > limit:
                        #print(f"  ❌ 비율 초과: {actual_ratio:.3f} > {limit}")
                        state["any_exceed"] = True
                        state["exceeded_nutrients"].append(nutrient)
                    else:
                        #print(f"  ✅ 비율 적정")
            # 일반적인 경우: 기준 초과 여부 확인 (Exceed)
            else:
                if actual > limit:
                    #print(f"  ❌ 기준 초과: {actual} > {limit}")
                    state["any_exceed"] = True
                    state["exceeded_nutrients"].append(nutrient)
                else:
                    #print(f"  ✅ 기준 이하")
        
        #print(f"\n=== 최종 결과 ===")
        #print(f"any_exceed: {state['any_exceed']}")
        #print(f"exceeded_nutrients: {state['exceeded_nutrients']}")
        #print(f"==================\n")

        return state


# 2. 알러지 분석


    def generate_allergy_prompt(self, product_key, final_profile_key, tone_key=None, max_new_tokens=512):
        """
        정의된 모듈의 Key 값을 받아 최적화된 시스템 프롬프트를 생성합니다.
        """
        # 2.1. 클래스 외부 변수 데이터 가져오기 (데이터가 없을 경우를 대비해 get 사용)
        p = products.get(str(product_key))
        f = final_profiles.get(str(final_profile_key))
        sub_rules = allergy_substitution_rules

        # 2.2. 예외 처리: 데이터가 없는 경우 None이 아닌 명확한 문자열 반환
        if not p or not f:
            return f"Error: 정보를 찾을 수 없습니다. (Product: {product_key}, Profile: {final_profile_key})"

        # 2.3. 시스템 프롬프트
        system_msg = f"""당신은 식품 성분 및 화학 분석 전문가입니다.
        주어진 원재료 리스트를 분석하여 사용자의 제한 사항('restricted_ingredients')과 대조하고 솔루션을 제공하세요.

        ### [Layer 1] 식약처 22종 마스터 리스트 기준
        분석 기준은 대한민국 식약처 고시 알레르기 유발 물질 22종입니다.

        ### [Layer 2] 원재료 추론 및 매핑 규칙
        1. 성분명에 직접적인 이름이 없더라도 '핵심 기원(Source) 물질'을 식별합니다. (예: '카제인나트륨' -> '우유')
        2. 대체 식재료는 다음 가이드를 참조하십시오:
        {sub_rules.get('rules', [])}

        ### [Layer 3] 분석 가이드라인
        - **Priority**: 1순위 알러지 차단 / 2순위 질환 영양 수치 충족 여부.
        - **Severity Level**: Critical(함유), Warning(교차 오염 가능성), Safe(무관) 분류.
        - ** 알러지를 유발할 수 있는 모든 원재료를 표시하세요.
        - ** 다른사람에게 알러지 가능성 있다 라는 식의 표현 사용하지 마세요.
        - ** 추론 규칙을 드러내지 마세요.
        - ** 반드시 아래의 json 형태로만 출력하세요. 주어진 json 컬럼 외에는 답변하지 마세요.


        ### [출력 형식]
        {{
          "ingredient_analysis": [
            {{
              "detected_ingredient": "성분명",
              "derived_from": "기원물질(22종 기준)",
              "substitute": "추천 대체재",
              "is_allergen": true
            }}
          ],
          "safety_summary": "최종 섭취 가능 여부 및 주의사항",
        }}

        [예시] few-shot
        {{
          "ingredient_analysis": [
            {{
              "detected_ingredient": "새우",
              "derived_from": "새우",
              "substitute": "흰살 생선, 버섯(킹오이스터), 두부",
              "is_allergen": false
            }}
          ],
          "safety_summary": "이 제품은 사용자의 알러지 항목인 우유와 땅콩을 포함하고 있지 않으므로 안전하게 섭취 가능합니다.",
        }}



        """

        # 2.4. 유저 프롬프트
        # 시스템 메시지의 변동성을 최소화하기 위해 동적데이터를 유저 메시지로 몰아넣습니다.
        user_msg = f"""
        [상품 정보]
        - 상품명: {p.get('name', '알 수 없음')}
        - 원재료: {p.get('ingerdients', [])}
        - 제조사 주의사항: {p.get('allergy', '없음')} / {p.get('trace', '없음')}

        [유저 프로필]
        - 제한 성분: {f.get('restricted_ingredients')}
        """



        messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
        ]



        # 3. llm 토크나이징
        # chat template 적용 → BatchEncoding 반환
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        attention_mask = inputs.get("attention_mask", None)
        if attention_mask is not None:
           attention_mask = attention_mask.to(self.model.device)

        with torch.no_grad():
             outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=attention_mask,
                max_new_tokens=max_new_tokens,
                temperature=0.1,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
        )

        # 프롬프트 길이 이후만 디코딩
        # 3.1. 질문의 길이를 잽니다.
        prompt_length = inputs["input_ids"].shape[-1]

        # 3.2. 슬라이싱: 전체 결과에서 10번째 이후부터만 가져옵니다.
        generated_ids = outputs[0][prompt_length:]

        # 3.3. 답변만 남은 generated_ids를 글자로 바꿉니다.
        raw_response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        # 디버깅: 원본 응답 출력
        #print(f"\n=== 원본 LLM 응답 ===")
        #print(raw_response)
        #print(f"===================\n")

        # overallState 초기화
        state: overallState = {
            "any_allergen": False,
            "substitute": []
        }

        try:
            # JSON 추출: 마크다운 코드 블록 제거 및 JSON 부분만 추출
            response_text = raw_response.strip()
            
            # 마크다운 코드 블록 제거 (```json ... ``` 형태)
            if response_text.startswith("```"):
                # 첫 번째 줄 제거
                lines = response_text.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                response_text = '\n'.join(lines)
            
            # 첫 번째 { 부터 마지막 } 까지 추출
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                print("Error: JSON 형식을 찾을 수 없습니다.")
                return state
            
            json_text = response_text[start_idx:end_idx+1]
            
            # 트레일링 콤마 제거 (JSON 파싱 에러의 흔한 원인)
            import re
            json_text = re.sub(r',\s*}', '}', json_text)
            json_text = re.sub(r',\s*]', ']', json_text)
            
            #print(f"\n=== 추출된 JSON ===")
            #print(json_text)
            #print(f"===================\n")
            
            # LLM의 출력이 JSON 형식이므로 파싱 시도
            data = json.loads(json_text)

            analysis = data.get("ingredient_analysis", [])

            # any_allergen 추출: 분석 결과 중 하나라도 true가 있으면 true
            state["any_allergen"] = any(item.get("is_allergen", False) for item in analysis)

            # any_allergen 추출: 분석 결과 중 하나라도 true가 있으면 true
            alle_list = []
            for item in analysis:
                # is_allergen이 true인 항목만 처리
                if item.get("is_allergen", False):
                    alle = item.get("derived_from", "")
                    if alle and alle != "없음":
                        # "생선, 두부" 처럼 문자열로 올 경우를 대비해 분리
                        alle_list.extend([s.strip() for s in alle.split(',')])

            state["allergen"] = list(set(alle_list))  # 중복 제거

            # substitute 추출: is_allergen이 true인 항목의 대체재만 수집 (중복 제거)
            sub_list = []
            for item in analysis:
                # is_allergen이 true인 항목만 처리
                if item.get("is_allergen", False):
                    sub = item.get("substitute", "")
                    if sub and sub != "없음":
                        # "생선, 두부" 처럼 문자열로 올 경우를 대비해 분리
                        sub_list.extend([s.strip() for s in sub.split(',')])

            state["substitute"] = list(set(sub_list))  # 중복 제거
            
            #print(f"\n=== 최종 파싱 결과 ===")
            #print(f"any_allergen: {state['any_allergen']}")
            #print(f"allergen: {state['allergen']}")
            #print(f"substitute: {state['substitute']}")
            #print(f"===================\n")

        except json.JSONDecodeError as e:
            print(f"Parsing Error: {e}")
            print(f"문제가 된 텍스트 (앞 200자): {json_text[:200] if 'json_text' in locals() else raw_response[:200]}")
            # 실패 시 기본 state 반환

        return state