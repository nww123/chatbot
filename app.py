from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import requests
import os
from dotenv import load_dotenv

# 加载环境变量（本地/部署都能用）
load_dotenv()

app = FastAPI()

# 挂载静态文件（必须指向 static 文件夹）
app.mount("/static", StaticFiles(directory="static"), name="static")


# 根路径返回聊天页面
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


# 聊天接口（POST 请求，和前端对应）
@app.post("/chat")
async def chat(request: Request):
    try:
        # 获取前端传的消息
        data = await request.json()
        user_message = data.get("message", "")

        # 千问接口配置（API Key 从环境变量取）
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            return {"error": "未配置 API Key"}

        # 调用千问接口
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-plus",
            "messages": [{"role": "user", "content": user_message}]
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 抛出 HTTP 错误
        result = response.json()

        # 提取回复
        reply = result["choices"][0]["message"]["content"]
        return {"reply": reply}

    except Exception as e:
        return {"error": f"请求失败：{str(e)}"}


# 本地运行入口
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)