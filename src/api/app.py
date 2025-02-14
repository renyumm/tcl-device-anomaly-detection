'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-11-14 15:19:29
LastEditTime: 2025-01-17 11:03:39
FilePath: /tcl-check-of-dirty-api/src/api/app.py
'''
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import routers


# 1、创建一个 FastAPI 实例
app = FastAPI(docs_url=None)    #app对象
app.mount("/src/api/css", StaticFiles(directory="./src/api/css"), name="css")   #挂载目录

# 2、声明一个 源 列表；重点：要包含跨域的客户端 源
origins = ["*"]

# 3、配置 CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)
    
# 路由
@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/src/api/css/swagger-ui-bundle.js",
        swagger_css_url="/src/api/css/swagger-ui.css",
        )


for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    import os
    os.environ['FACTORY'] = 'dw3'
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=28000)