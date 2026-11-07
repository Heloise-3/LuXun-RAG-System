"""Same-origin FastAPI web application. No provider calls occur at startup."""
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import APIError, APITimeoutError
from pydantic import BaseModel, Field, ValidationError
from config import ROOT, ConfigurationError
from rag import generate_with_rag

app = FastAPI(title='Lu Xun Writing Lab', version='0.2.0')
# Keep an individual app process from accumulating paid requests.
_slots = threading.BoundedSemaphore(2)

class GenerateRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=2, ge=1, le=5)

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/api/generate')
def generate(payload: GenerateRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(422, '请输入写作主题或待改写文字。')
    if not _slots.acquire(blocking=False):
        raise HTTPException(429, '服务忙，请稍后重试。')
    try:
        return generate_with_rag(query, payload.top_k)
    except ConfigurationError as exc:
        raise HTTPException(503, str(exc)) from None
    except APITimeoutError:
        raise HTTPException(504, '模型服务响应超时，请稍后重试。') from None
    except APIError:
        raise HTTPException(502, '模型服务暂不可用，请检查服务端配置、余额与模型权限。') from None
    except (ValueError, ValidationError, OSError, KeyError, TypeError):
        raise HTTPException(503, '语料索引或模型返回格式无效，请联系维护者检查。') from None
    except Exception:
        raise HTTPException(500, '生成失败，请稍后重试。') from None
    finally:
        _slots.release()

@app.get('/')
def index():
    return FileResponse(ROOT / 'frontend' / 'index.html')

app.mount('/static', StaticFiles(directory=ROOT / 'frontend'), name='static')
