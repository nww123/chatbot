import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

# 初始化配置
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise RuntimeError("请配置环境变量 DASHSCOPE_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
app = FastAPI()

# 挂载静态文件 & 主页直接返回聊天页面
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


# 核心聊天接口
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")

    if not user_msg:
        return JSONResponse({"error": "消息不能为空"}, status_code=400)

    # 调用千问模型
    resp = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": user_msg}]
    )
    return {"reply": resp.choices[0].message.content}


# 启动服务
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 8000)))