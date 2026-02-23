import streamlit as st
import requests
import json
import os
# 👇 [修改点 1] 引入核心逻辑类，方便云端直接调用
from brain import IndustrialBrain

# --- 页面配置 ---
st.set_page_config(
    page_title="Aether-1 工业智脑",
    page_icon="🏭",
    layout="wide"
)

# --- 样式美化 ---
st.markdown("""
<style>
    .risk-high { background-color: #ff4b4b; padding: 10px; border-radius: 5px; color: white; }
    .risk-medium { background-color: #ffa421; padding: 10px; border-radius: 5px; color: white; }
    .risk-low { background-color: #21c354; padding: 10px; border-radius: 5px; color: white; }
</style>
""", unsafe_allow_html=True)

# --- 侧边栏 ---
with st.sidebar:
    st.header("🎛️ 现场模拟器 (IoT Simulator)")
    st.subheader("传感器读数")
    temp = st.slider("温度 (°C)", 0.0, 120.0, 45.0, format="%.1f")
    vibration = st.slider("震动 (mm/s)", 0.0, 10.0, 1.2, format="%.1f")
    humidity = st.slider("湿度 (%)", 0, 100, 30)

    st.subheader("视觉检测 (Vision)")
    vision_options = [
        "Everything normal. Workers present.",
        "Smoke detected near generator.",
        "Unknown intruder in restricted area.",
        "Sparks visible from main cable.",
        "Worker not wearing safety helmet."
    ]
    vision_text = st.selectbox("选择或输入视觉描述:", vision_options)
    custom_vision = st.text_input("自定义视觉描述 (可选)", "")
    if custom_vision:
        vision_text = custom_vision

    st.markdown("---")
    analyze_btn = st.button("🚀 发送数据给 AI", type="primary", use_container_width=True)

# --- 主界面 ---
st.title("🏭 Aether-1 工业安全监控中心")
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📡 实时数据流")
    st.metric("核心温度", f"{temp} °C", delta=f"{temp - 80:.1f}" if temp > 80 else "Normal", delta_color="inverse")
    st.metric("震动幅度", f"{vibration} mm/s", delta=f"{vibration - 5.0:.1f}" if vibration > 5 else "Stable",
              delta_color="inverse")
    st.info(f"👁️ 视觉反馈: {vision_text}")

with col2:
    st.subheader("🧠 AI 决策引擎")

    if analyze_btn:
        # 构建请求数据
        payload = {
            "sensor_data": {
                "temperature": temp,
                "vibration": vibration,
                "humidity": humidity
            },
            "vision_text": vision_text
        }

        with st.spinner("DeepSeek 正在分析多模态数据..."):
            result = None  # 初始化结果容器

            # 👇 [修改点 2] 智能切换逻辑：先试 API，失败则转本地调用
            try:
                # 尝试连接 FastAPI (设置 1 秒超时，连不上立刻切换)
                response = requests.post("http://127.0.0.1:8000/api/analyze", json=payload, timeout=1)
                if response.status_code == 200:
                    result = response.json()
                    st.toast("已连接到后端 API (Local Mode)", icon="🔌")
            except:
                # API 连接失败，进入 Serverless 模式 (直接调用 Python 类)
                # 这在 Streamlit Cloud 部署时非常有用
                try:
                    brain = IndustrialBrain()
                    result = brain.analyze_situation(payload["sensor_data"], payload["vision_text"])
                    st.toast("已切换至云端直连模式 (Serverless Mode)", icon="☁️")
                except Exception as e:
                    st.error(f"AI 核心启动失败: {str(e)}")

            # 👇 [这里往下全部保持不变] 只要拿到 result，渲染逻辑是一样的
            if result:
                # 1. 显示风险等级
                risk = result.get("risk_level", "UNKNOWN")
                if risk == "HIGH":
                    st.markdown(f'<div class="risk-high">🚨 风险等级: 高危 (HIGH)</div>', unsafe_allow_html=True)
                elif risk == "MEDIUM":
                    st.markdown(f'<div class="risk-medium">⚠️ 风险等级: 警告 (MEDIUM)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="risk-low">✅ 风险等级: 安全 (LOW)</div>', unsafe_allow_html=True)

                # 2. 显示分析结果
                st.markdown(f"### 🧐 事故分析")
                st.write(result.get("analysis"))

                # 3. 显示设备动作指令
                st.markdown(f"### 🛠️ 设备控制指令")
                actions = result.get("actions", [])
                st.dataframe(actions, use_container_width=True)

                # 4. 原始数据
                with st.expander("查看原始 JSON 响应"):
                    st.json(result)