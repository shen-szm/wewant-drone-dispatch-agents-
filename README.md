# WeWant Drone Dispatch Multi-Agent System

基于多 Agent 协作的无人机物流智能调度与监控中枢原型。

## 架构说明
本项目采用 Python + Flask-SocketIO 构建后端，前端采用 Leaflet.js 进行地理信息可视化。
系统内包含四大核心 Agent 协同工作：
1. **订单解析 Agent**：结构化提取任务池数据。
2. **航线规划 Agent**：长链推理（结合载重、气象）动态生成 3D 航线。
3. **冲突仲裁 Agent**：全局空间交汇预警机制。
4. **前端通讯 Agent**：高频遥测数据流式推送。

## 快速启动

1. 安装依赖：
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. 运行调度中枢：
\`\`\`bash
python app.py
\`\`\`

3. 打开浏览器访问：`http://localhost:5000` 即可查看实时调度地图与无人机飞行轨迹。

## UI / 设计说明
* 前端采用了深色高对比度底图 (`cartocdn/dark_all`)，符合简约高级的可视化设计规范。
* 飞行器的轨迹图标已通过 JavaScript 层的向量运算，严格校准了实时偏航角 (Bearing)，解决了静态图标与实际航线方向背离的问题。
* 预留了 `static/` 目录，未来可直接替换去文字版的纯几何品牌 Logo 资产。
