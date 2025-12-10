from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

from samba import llm

app = FastAPI()


async def llm_response_generator(body: dict, api_key: str):
    response = llm(body, api_key, True)
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            yield data + "\n\n"


@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not api_key:
        raise HTTPException(status_code=401, detail="api_key cannot be empty")

    return StreamingResponse(
        llm_response_generator(body, api_key),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
