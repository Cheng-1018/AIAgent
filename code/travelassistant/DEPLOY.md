# 智能旅行助手 - Docker部署指南

## 快速部署

### 1. 准备工作

确保服务器已安装：
- Docker (20.10+)
- Docker Compose (1.29+)

安装Docker：
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# CentOS
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

安装Docker Compose：
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 上传项目文件

将项目上传到服务器：
```bash
# 方法1: 使用scp
scp -r travelassistant/ user@server:/home/user/

# 方法2: 使用git
ssh user@server
git clone <your-repo-url>
cd travelassistant
```

### 3. 配置环境变量

编辑`.env`文件，确保所有API密钥正确：
```bash
vi .env
```

### 4. 部署服务

#### 方法1: 使用自动部署脚本（推荐）
```bash
chmod +x deploy.sh
./deploy.sh
```

#### 方法2: 手动部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 5. 验证部署

访问服务：
```bash
curl http://localhost:8000/health
```

或在浏览器打开：`http://your-server-ip:8000`

## 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看最近50行
docker-compose logs --tail=50
```

### 重启服务
```bash
docker-compose restart
```

### 停止服务
```bash
docker-compose stop
```

### 停止并删除容器
```bash
docker-compose down
```

### 重新构建并启动
```bash
docker-compose up -d --build
```

### 进入容器
```bash
docker-compose exec travelassistant bash
```

### 更新代码
```bash
# 拉取最新代码
git pull

# 重新构建和启动
docker-compose up -d --build
```

## 性能优化

### 1. 使用Nginx反向代理

创建`nginx.conf`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 配置HTTPS

使用Let's Encrypt获取免费SSL证书：
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 设置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw enable

# CentOS
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## 监控和维护

### 查看资源使用
```bash
docker stats
```

### 清理Docker资源
```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理所有未使用的资源
docker system prune -a
```

### 备份数据
```bash
# 导出容器
docker export travel-assistant > travel-assistant-backup.tar

# 导出镜像
docker save travel-assistant:latest > travel-assistant-image.tar
```

### 恢复数据
```bash
# 导入容器
docker import travel-assistant-backup.tar

# 导入镜像
docker load < travel-assistant-image.tar
```

## 故障排查

### 容器无法启动
```bash
# 查看详细日志
docker-compose logs --tail=100

# 检查容器状态
docker-compose ps

# 查看容器内部
docker-compose exec travelassistant bash
```

### 端口被占用
```bash
# 查看端口占用
sudo lsof -i :8000

# 或
sudo netstat -tulpn | grep 8000

# 修改docker-compose.yml中的端口映射
ports:
  - "8080:8000"  # 改为其他端口
```

### 内存不足
在`docker-compose.yml`中限制资源：
```yaml
services:
  travelassistant:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### API调用失败
1. 检查网络连接
2. 验证API密钥是否正确
3. 检查服务器防火墙设置

## 生产环境建议

1. **使用环境变量管理敏感信息**，不要将API密钥硬编码
2. **启用HTTPS**，保护数据传输安全
3. **配置日志轮转**，避免日志文件过大
4. **定期备份**重要数据
5. **监控服务状态**，使用工具如Prometheus + Grafana
6. **设置资源限制**，防止服务占用过多资源
7. **使用CDN**加速静态资源加载

## 扩展部署

### 多实例负载均衡

修改`docker-compose.yml`：
```yaml
services:
  travelassistant:
    build: .
    deploy:
      replicas: 3
    # ...其他配置
```

### 使用外部数据库

如果需要持久化存储，可以添加数据库服务：
```yaml
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: your_password
    volumes:
      - pgdata:/var/lib/postgresql/data
```

## 技术支持

如有问题，请查看：
1. 项目日志：`docker-compose logs`
2. GitHub Issues
3. 项目文档

## 安全建议

1. 定期更新Docker镜像
2. 使用非root用户运行容器
3. 限制容器的网络访问
4. 定期扫描漏洞：`docker scan travel-assistant:latest`
5. 不要在`.env`文件中使用弱密码
