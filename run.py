from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from samba import llm
from uuid import uuid4
import time
import json

app = FastAPI()


async def llm_response_generator(body: dict):
    response = llm(body, True)
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            yield data + "\n\n"


def llm_response(body: dict):
    response = llm(body, False)
    if response.status_code == 200:
        return response.json()
    else:
        response = llm(body, True)
        content = ""
        usage = {}
        if response.status_code != 200:
            raise Exception(response.text)
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8").replace("data:", "").strip()
                if data.startswith("{"):
                    data = json.loads(data)
                    if data.get("choices"):
                        content += data["choices"][0]["delta"]["content"]
                    if data.get("usage", False):
                        usage = data["usage"]
        return {
            "id": str(uuid4()).replace("-", ""),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": body.get("model", "unknown"),
            "usage": usage,
            "choices": [
                {
                    "message": {
                        "content": content,
                        "refusal": None,
                        "role": "assistant",
                        "audio": None,
                        "function_call": None,
                        "tool_calls": None
                    },
                    "logprobs": None,
                    "finish_reason": "stop",
                    "index": 0
                }
            ]
        }


@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    is_stream = body.get("stream", False)
    if is_stream:
        return StreamingResponse(
            llm_response_generator(body),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        return llm_response(body)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
