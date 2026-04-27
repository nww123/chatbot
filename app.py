import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

# 初始化配置（读取阿里云百炼API密钥）
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise RuntimeError("请先配置环境变量 DASHSCOPE_API_KEY")

# 初始化OpenAI客户端（兼容千问模型）
client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# 初始化FastAPI应用
app = FastAPI()

# 配置跨域（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（前端页面）
app.mount("/static", StaticFiles(directory="static"), name="static")


# 健康检查接口
@app.get("/health")
async def health():
    return {"status": "ok"}


# 主页：返回前端聊天页面
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


# 核心聊天接口：接收用户消息，调用千问模型返回回复
@app.post("/chat")
async def chat(request: Request):
    # 解析用户发送的JSON数据
    data = await request.json()
    # 获取用户消息
    user_msg = data.get("message", "")

    # 空消息校验（最基础的校验）
    if not user_msg:
        return JSONResponse({"error": "消息不能为空"}, status_code=400)

    # 调用千问模型并返回结果
    resp = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": user_msg}]
    )
    return {"reply": resp.choices[0].message.content}


# 启动服务
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)