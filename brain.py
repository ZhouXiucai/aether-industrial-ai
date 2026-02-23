import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
from colorama import Fore, Style, init

# 初始化
load_dotenv()
init(autoreset=True)  # 让控制台输出带颜色


class IndustrialBrain:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        # DeepSeek V3 (deepseek-chat) 性价比最高，适合高频调用
        self.model = "deepseek-chat"

    def analyze_situation(self, sensor_data: dict, vision_text: str):
        """
        发送数据给 DeepSeek 进行决策
        """
        print(f"{Fore.CYAN}📡 正在同步数据到 DeepSeek Cloud...")

        # --- Prompt Engineering ---
        # 技巧：在 System Prompt 中定义严格的 JSON Schema
        system_prompt = """
        你是一个工业安全控制系统 (Aether-1)。
        你的任务是根据【传感器数据】和【视觉描述】判断现场风险等级。

        必须且只能输出如下 JSON 格式，严禁包含任何 Markdown 格式或额外废话：
        {
            "risk_level": "LOW" | "MEDIUM" | "HIGH",
            "analysis": "简短的分析（50字以内）",
            "actions": [
                {"device": "FAN", "state": "ON" | "OFF"},
                {"device": "ALARM", "state": "ON" | "OFF"},
                {"device": "MAIN_POWER", "state": "ON" | "OFF"}
            ]
        }
        """

        user_content = f"""
        [当前状态]
        - 传感器读数: {json.dumps(sensor_data)}
        - 视觉检测结果: "{vision_text}"

        [安全阈值参考]
        - 温度 > 80°C 为危险
        - 震动 > 5.0mm/s 为危险
        - 视觉发现 "fire", "smoke", "intruder" 为极度危险
        """

        try:
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.1,  # 降低随机性，工业控制要求稳定
                max_tokens=500
            )

            duration = time.time() - start_time
            raw_content = response.choices[0].message.content

            print(f"{Fore.GREEN}✅ DeepSeek 响应 ({duration:.2f}s):")
            # print(raw_content) # 调试时可以打开

            # --- 数据清洗 ---
            # 有时候模型会手贱加上 ```json ... ```，我们需要去掉
            clean_json = raw_content.replace("```json", "").replace("```", "").strip()

            return json.loads(clean_json)

        except json.JSONDecodeError:
            print(f"{Fore.RED}❌ JSON 解析失败，AI 返回了非结构化数据")
            return None
        except Exception as e:
            print(f"{Fore.RED}❌ API 调用错误: {e}")
            return None