#!/bin/bash

# 智能旅行助手 - 部署脚本

set -e

echo "======================================"
echo "智能旅行助手 - 自动部署脚本"
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装，请先安装Docker${NC}"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装，请先安装Docker Compose${NC}"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${RED}错误: .env文件不存在${NC}"
    echo "请创建.env文件并配置API密钥"
    exit 1
fi

echo -e "${GREEN}✓ 环境检查通过${NC}"

# 停止旧容器
echo -e "${YELLOW}停止旧容器...${NC}"
docker-compose down || true

# 清理旧镜像（可选）
read -p "是否清理旧镜像? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}清理旧镜像...${NC}"
    docker-compose down --rmi all || true
fi

# 构建镜像
echo -e "${YELLOW}构建Docker镜像...${NC}"
docker-compose build

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 5

# 检查服务状态
echo -e "${YELLOW}检查服务状态...${NC}"
docker-compose ps

# 测试健康检查
echo -e "${YELLOW}测试服务健康状态...${NC}"
sleep 3
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 服务启动成功！${NC}"
    echo -e "${GREEN}访问地址: http://localhost:8000${NC}"
else
    echo -e "${RED}✗ 服务启动失败，请查看日志${NC}"
    docker-compose logs --tail=50
    exit 1
fi

# 显示日志
echo ""
echo -e "${YELLOW}实时日志 (Ctrl+C退出):${NC}"
docker-compose logs -f
