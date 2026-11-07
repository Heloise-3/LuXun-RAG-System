"""Configuration is loaded without printing credentials or creating clients on import."""
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env', override=False)

class ConfigurationError(RuntimeError):
    pass

def model_name():
    return os.getenv('DEEPSEEK_MODEL', 'deepseek-flash')

def make_client(provider):
    key_name, url = {
        'deepseek': ('DEEPSEEK_API_KEY', 'https://api.deepseek.com'),
        'siliconflow': ('SILICONFLOW_API_KEY', 'https://api.siliconflow.cn/v1'),
    }[provider]
    key = os.getenv(key_name)
    if not key:
        raise ConfigurationError(f'请在服务端配置 {key_name}。')
    return OpenAI(api_key=key, base_url=os.getenv(f'{provider.upper()}_BASE_URL', url),
                  timeout=25.0, max_retries=0)
