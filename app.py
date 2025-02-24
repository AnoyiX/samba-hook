from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

from samba import llm

app = FastAPI()


async def llm_response_generator(body: dict):
    response = llm(body, True)
    for line in response.iter_lines():
        if line:
            data = line.decode('utf-8').replace('data: ', '')
            yield data


def llm_response(body: dict):
    response = llm(body, False)
    return response.json()


@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    is_stream = body.get('stream', False)
    if is_stream:
        async def event_generator():
            async for data in llm_response_generator(body):
                if await request.is_disconnected():
                    break
                yield {"data": data}
        return EventSourceResponse(event_generator())
    else:
        return llm_response(body)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
