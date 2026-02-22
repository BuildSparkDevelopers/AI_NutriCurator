# app/infra/llm/loader.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelLoader:
    _instances = {}

    @classmethod
    def get_model_and_tokenizer(cls, model_name: str, device: str = "auto"):
        """
        모델 이름을 키로 사용하여 이미 로드된 모델이 있다면 재사용하고, 
        없다면 새로 로드하여 반환합니다.
        """
        if model_name not in cls._instances:
            print(f"--- [{model_name}] 모델을 로드합니다. ---")
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map=device,
                trust_remote_code=True
            )
            model.eval()
            
            cls._instances[model_name] = (model, tokenizer)
        
        return cls._instances[model_name]

def get_agent_model_config(agent_name: str):
    """
    에이전트별 특성에 따른 모델 설정을 반환합니다.
    (예: 복잡한 추론이 필요한 ORCH는 더 큰 모델, 단순 요약은 작은 모델)
    """
    configs = {
        "CHATagent": {"model_name": "Qwen/Qwen2.5-14B-Instruct", "temp": 0.7},
        "ORCHagent": {"model_name": "Qwen/Qwen2.5-32B-Instruct", "temp": 0.1}, # 정확한 판단 필요
        "USERagent": {"model_name": "Qwen/Qwen2.5-14B-Instruct", "temp": 0.2},
        "RECOagent": {"model_name": "Qwen/Qwen2.5-14B-Instruct", "temp": 0.3},
        "RESPagent": {"model_name": "Qwen/Qwen2.5-14B-Instruct", "temp": 0.8}, # 창의적 문장 생성
    }
    # 목록에 없는 에이전트는 기본 설정 반환
    return configs.get(agent_name, {"model_name": "Qwen/Qwen2.5-14B-Instruct", "temp": 0.5})