from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import logging
from typing import List

# 導入數據庫相關模塊
from database.session import get_db, init_db

# 導入API路由
from .routers import documents, questions, categories, search

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("knowledge_api")

# 創建FastAPI應用
app = FastAPI(
    title="Knowledge API",
    description="Knowledge系統API，用於管理知識文檔和問答功能",
    version="1.0.0",
)

# 配置CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    # 添加其他允許的源
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

# 掛載靜態文件
app.mount("/static", StaticFiles(directory="static"), name="static")


# 啟動事件
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Knowledge API")
    # 初始化數據庫
    init_db()
    logger.info("Database initialized")


# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Knowledge API")


# 健康檢查端點
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "knowledge_api"}


# 根路由
@app.get("/")
async def root():
    return {"message": "Welcome to Knowledge API"}


# 全局異常處理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# 運行應用（僅在直接執行此文件時）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)