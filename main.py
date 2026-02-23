import time
from brain import IndustrialBrain
from colorama import Fore


def main():
    brain = IndustrialBrain()

    # --- 场景 1: 平平无奇的下午 ---
    print(f"\n{Fore.YELLOW}--- 测试场景 1: 设备正常运转 ---")
    sensors_1 = {"temperature": 45.2, "vibration": 1.2, "humidity": 30}
    vision_1 = "No anomaly detected. Workers are operating normally."

    result_1 = brain.analyze_situation(sensors_1, vision_1)
    if result_1:
        print(f"🧐 AI 分析: {result_1['analysis']}")
        print(f"🛠  执行指令: {result_1['actions']}")

    time.sleep(2)  # 模拟间隔

    # --- 场景 2: 突发状况！ ---
    print(f"\n{Fore.RED}--- 测试场景 2: 模拟突发火情 ---")
    sensors_2 = {"temperature": 88.5, "vibration": 6.8, "humidity": 10}
    # 这里模拟 YOLO 检测到了火光
    vision_2 = "Detected bright flashing light and black smoke in sector A."

    result_2 = brain.analyze_situation(sensors_2, vision_2)
    if result_2:
        print(f"😱 AI 分析: {result_2['analysis']}")
        print(f"🚨 执行指令: {result_2['actions']}")

        # 简单的逻辑验证
        if result_2['risk_level'] == 'HIGH':
            print(f"{Fore.RED}>>> 紧急协议启动！物理切断电源！ <<<")


if __name__ == "__main__":
    main()