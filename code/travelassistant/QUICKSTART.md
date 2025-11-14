# 快速启动指南

## 安装步骤

### 1. 安装Python依赖

```bash
# 在项目根目录下
pip install -r requirements.txt
```

### 2. 确保Node.js已安装

MCP服务需要Node.js环境，请确保已安装Node.js 16+版本。

检查Node.js版本：
```bash
node --version
npm --version
```

如未安装，请访问 https://nodejs.org/ 下载安装。

### 3. 配置环境变量

项目已包含`.env`文件，里面有所有必需的API密钥配置。如果需要修改，请编辑`.env`文件。

### 4. 启动服务

```bash
# 方法1: 直接运行
cd backend
python run.py

# 方法2: 使用uvicorn
cd backend
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问应用

打开浏览器访问：http://localhost:8000

## 测试API

### 使用curl测试

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试行程规划
curl -X POST http://localhost:8000/api/plan \
  -H "Content-Type: application/json" \
  -d '{
    "city": "北京",
    "start_date": "2025-06-01",
    "end_date": "2025-06-03",
    "travel_days": 3,
    "transportation": "公共交通",
    "accommodation": "经济型酒店",
    "preferences": ["历史文化", "美食"],
    "free_text_input": "想看升旗"
  }'

# 测试POI搜索
curl -X POST http://localhost:8000/api/poi/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "故宫",
    "city": "北京",
    "citylimit": true
  }'

# 测试天气查询
curl http://localhost:8000/api/weather/北京
```

### 使用Postman或其他API工具

导入以下请求到你喜欢的API测试工具：

**POST** http://localhost:8000/api/plan
```json
{
  "city": "北京",
  "start_date": "2025-06-01",
  "end_date": "2025-06-03",
  "travel_days": 3,
  "transportation": "公共交通",
  "accommodation": "经济型酒店",
  "preferences": ["历史文化", "美食"],
  "free_text_input": "想看升旗"
}
```

## 常见问题

### 1. 导入错误

如果遇到模块导入错误，请确保：
- 已安装所有依赖：`pip install -r requirements.txt`
- 在正确的目录下运行：应在`backend`目录下运行`python run.py`

### 2. MCP连接失败

错误信息：`MCP service connection failed`

解决方法：
- 确认Node.js已安装
- 确认高德地图API密钥正确
- 检查网络连接
- 第一次运行会自动安装MCP服务器，请耐心等待

### 3. 端口被占用

错误信息：`Address already in use`

解决方法：
- 修改`.env`文件中的`API_PORT`为其他端口
- 或者结束占用8000端口的进程

### 4. CORS错误

如果前端无法访问API，请确保：
- 前端通过`http://localhost:8000`访问（不要用其他端口）
- 如需使用其他端口，请在`config.py`的`CORS_ORIGINS`中添加

### 5. API密钥无效

如果API调用失败，请检查`.env`文件中的API密钥是否正确：
- `LLM_API_KEY`: Silicon Flow API密钥
- `AMAP_API_KEY`: 高德地图API密钥
- `UNSPLASH_ACCESS_KEY`: Unsplash访问密钥

## 开发模式

启用热重载（代码修改后自动重启）：

```bash
cd backend
python run.py
```

或者：

```bash
cd backend
uvicorn app.api.main:app --reload
```

## 生产部署

### 使用Docker (推荐)

```dockerfile
# 创建Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装Node.js
RUN apt-get update && apt-get install -y nodejs npm

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY .env .

WORKDIR /app/backend

EXPOSE 8000

CMD ["python", "run.py"]
```

构建和运行：
```bash
docker build -t travel-assistant .
docker run -p 8000:8000 travel-assistant
```

### 使用Gunicorn

```bash
pip install gunicorn
cd backend
gunicorn app.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 性能优化建议

1. **使用缓存**: 对频繁查询的数据（如热门景点、天气）使用Redis缓存
2. **连接池**: 配置数据库连接池和HTTP连接池
3. **异步处理**: 充分利用FastAPI的异步特性
4. **CDN**: 将前端静态资源部署到CDN
5. **负载均衡**: 使用Nginx进行负载均衡

## 监控和日志

添加日志记录：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 安全建议

1. 不要将`.env`文件提交到Git仓库
2. 在生产环境使用HTTPS
3. 配置速率限制防止API滥用
4. 定期更新依赖包
5. 使用环境变量管理敏感信息

## 技术支持

如遇到问题，请：
1. 查看终端输出的错误信息
2. 检查`requirements.txt`中的依赖版本
3. 确认所有API密钥有效
4. 提交Issue到GitHub仓库

祝您使用愉快！🎉
