from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from brain import IndustrialBrain

# 1. 初始化 APP
app = FastAPI(title="Aether-1 Industrial AI Backend")

# 2. 解决跨域问题 (CORS) - 允许前端访问后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许任何来源访问 (开发环境用 *，生产环境要指定域名)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 初始化 AI 大脑 (在服务启动时加载，避免每次请求都重新初始化)
brain_engine = IndustrialBrain()


# 4. 定义数据模型 (Pydantic) - 相当于数据验证门卫
class SensorData(BaseModel):
    temperature: float
    vibration: float
    humidity: float


class InspectionRequest(BaseModel):
    sensor_data: SensorData
    vision_text: str  # 边缘端(YOLO)传来的文字描述


# 5. 定义 API 接口
@app.get("/")
def home():
    return {"status": "Online", "system": "Aether-1 DeepSeek Core"}


@app.post("/api/analyze")
def analyze_risk(request: InspectionRequest):
    """
    接收传感器数据 + 视觉描述 -> 返回 AI 决策
    """
    print(f"📥 收到请求: Temp={request.sensor_data.temperature}, Vision={request.vision_text}")

    # 调用我们在 brain.py 里写的逻辑
    # 注意：要把 Pydantic 对象转回 dict 传给 brain
    result = brain_engine.analyze_situation(
        request.sensor_data.dict(),
        request.vision_text
    )

    if not result:
        raise HTTPException(status_code=500, detail="DeepSeek 响应失败")

    return result


# 6. 启动入口
if __name__ == "__main__":
    # host="0.0.0.0" 意味着允许局域网访问 (方便你用手机或 ESP32 测试)
    uvicorn.run(app, host="0.0.0.0", port=8000)