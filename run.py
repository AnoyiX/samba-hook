from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from samba import llm

app = FastAPI()


async def llm_response_generator(body: dict):
    response = llm(body, True)
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            yield data + "\n\n"


@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    return StreamingResponse(
        llm_response_generator(body),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
