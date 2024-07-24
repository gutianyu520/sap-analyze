from fastapi import FastAPI
from api import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# 路由
app.include_router(api_router)

# 配置信息
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     #允许的来源
    allow_credentials=True,  #允许凭据
    allow_methods=["*"],     #允许的 HTTP 方法
    allow_headers=["*"],     #允许的 HTTP 头信息
    # expose_headers=["X-Custom-Header"],  #公开的 HTTP 头信息
    max_age=3600,            #预检请求的最大时间

)


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
