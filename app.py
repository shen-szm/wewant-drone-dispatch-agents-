import time
import math
import eventlet
from flask import Flask, render_template
from flask_socketio import SocketIO
from dataclasses import dataclass
from typing import List, Optional

# 初始化 Flask 与 WebSocket
eventlet.monkey_patch()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# --- 数据结构 ---
@dataclass
class Order:
    order_id: str
    weight_kg: float
    target_coords: tuple
    
@dataclass
class Drone:
    drone_id: str
    max_payload_kg: float
    current_coords: tuple
    status: str

@dataclass
class Route:
    route_id: str
    drone_id: str
    waypoints: List[tuple]

# --- 多 Agent 定义 ---
class OrderParsingAgent:
    def parse(self, raw_data: dict) -> Order:
        return Order(raw_data['id'], raw_data['weight'], raw_data['destination'])

class RoutingAgent:
    def chain_reasoning_route(self, order: Order, drones: List[Drone]) -> Optional[Route]:
        # 挑选无人机
        available = [d for d in drones if d.status == "IDLE" and d.max_payload_kg >= order.weight_kg]
        if not available: return None
        selected = available[0]
        
        # 简单的长链推理：起点 -> 巡航高度层 -> 终点
        start = selected.current_coords
        end = order.target_coords
        # 模拟生成 20 个途径点以实现平滑移动动画
        waypoints = []
        steps = 20
        for i in range(steps + 1):
            lat = start[0] + (end[0] - start[0]) * (i / steps)
            lng = start[1] + (end[1] - start[1]) * (i / steps)
            waypoints.append((lat, lng, 60)) # 60m 巡航高度
            
        return Route(f"RT_{order.order_id}", selected.drone_id, waypoints)

class ArbitrationAgent:
    def check_conflicts(self, route: Route) -> bool:
        return True # 原型中默认安全通过

# --- 全局状态与模拟引擎 ---
fleet = [Drone("UAV_001", 5.0, (23.1200, 113.2800), "IDLE")]
order_agent = OrderParsingAgent()
routing_agent = RoutingAgent()
arbitrator = ArbitrationAgent()

def simulation_loop():
    """后台任务：模拟订单产生并驱动无人机飞行"""
    while True:
        # 1. 模拟收到新订单
        raw_order = {"id": f"ORD_{int(time.time())}", "weight": 2.5, "destination": (23.1350, 113.2950)}
        print(f"📦 新订单接入: {raw_order['id']}")
        
        order = order_agent.parse(raw_order)
        route = routing_agent.chain_reasoning_route(order, fleet)
        
        if route and arbitrator.check_conflicts(route):
            fleet[0].status = "IN_FLIGHT"
            # 2. 模拟沿着途径点飞行，并通过 WebSocket 推送
            for wp in route.waypoints:
                payload = {
                    "type": "FLIGHT_UPDATE",
                    "drone_id": route.drone_id,
                    "position": wp
                }
                socketio.emit('telemetry', payload)
                time.sleep(0.5) # 控制前端移动速度
            
            # 飞行结束，重置状态并返航（原型简化为直接重置坐标）
            fleet[0].status = "IDLE"
            fleet[0].current_coords = (23.1200, 113.2800)
            socketio.emit('telemetry', {"type": "FLIGHT_UPDATE", "drone_id": route.drone_id, "position": fleet[0].current_coords})
        
        time.sleep(3) # 等待 3 秒后接下一个单

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # 启动后台模拟线程
    socketio.start_background_task(simulation_loop)
    print("🚀 调度中心已启动: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
