# CareerNavigator 部署指南

本文档详细介绍了 CareerNavigator 智能职业规划系统的部署方法，包括本地开发、测试环境和生产环境的完整部署流程。

## 目录

1. [环境准备](#环境准备)
2. [本地开发部署](#本地开发部署)
3. [测试环境部署](#测试环境部署)
4. [生产环境部署](#生产环境部署)
5. [配置管理](#配置管理)
6. [监控与维护](#监控与维护)
7. [故障排除](#故障排除)

## 环境准备

### 系统要求

**最低配置要求：**
- CPU: 2核心
- 内存: 4GB RAM
- 存储: 20GB 可用空间
- 操作系统: Ubuntu 20.04+ / CentOS 7+ / macOS 10.15+

**推荐配置：**
- CPU: 4核心
- 内存: 8GB RAM
- 存储: 50GB SSD
- 网络: 稳定的互联网连接

### 软件依赖

**必需软件：**
- Python 3.11 或更高版本
- Node.js 20.x 或更高版本
- pnpm 包管理器
- Git 版本控制

**可选软件：**
- Docker (用于容器化部署)
- Nginx (用于反向代理)
- PM2 (用于进程管理)

### 安装基础软件

**Ubuntu/Debian 系统：**
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# 安装 Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 pnpm
npm install -g pnpm

# 安装 Git
sudo apt install git -y
```

**CentOS/RHEL 系统：**
```bash
# 安装 EPEL 仓库
sudo yum install epel-release -y

# 安装 Python 3.11
sudo yum install python3.11 python3.11-devel python3.11-pip -y

# 安装 Node.js 20
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install nodejs -y

# 安装 pnpm
npm install -g pnpm

# 安装 Git
sudo yum install git -y
```

**macOS 系统：**
```bash
# 使用 Homebrew 安装
brew install python@3.11 node@20 git

# 安装 pnpm
npm install -g pnpm
```

## 本地开发部署

### 1. 获取项目代码

```bash
# 克隆项目仓库
git clone <repository-url>
cd career_navigator_project

# 查看项目结构
ls -la
```

### 2. 后端环境设置

```bash
# 进入后端目录
cd career_navigator_backend

# 创建并激活虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或者在 Windows 上使用: venv\Scripts\activate

# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import langgraph, dashscope, flask; print('所有依赖安装成功')"
```

### 3. 前端环境设置

```bash
# 进入前端目录
cd ../career_navigator_frontend

# 安装依赖
pnpm install

# 验证安装
pnpm list
```

### 4. 环境变量配置

创建环境变量文件：

```bash
# 在项目根目录创建 .env 文件
cd ..
cat > .env << EOF
# 阿里云百炼 API 配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# Flask 应用配置
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# 数据库配置（可选）
DATABASE_URL=sqlite:///career_navigator.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
EOF
```

**获取阿里云百炼 API 密钥：**

1. 访问 [阿里云百炼控制台](https://dashscope.console.aliyun.com/)
2. 注册并登录阿里云账号
3. 开通百炼服务
4. 在 API 密钥管理页面创建新的 API 密钥
5. 将密钥复制到 `.env` 文件中

### 5. 启动开发服务

**启动后端服务：**
```bash
# 在第一个终端窗口
cd career_navigator_backend
source venv/bin/activate
export DASHSCOPE_API_KEY="your_api_key_here"
python src/main.py
```

**启动前端服务：**
```bash
# 在第二个终端窗口
cd career_navigator_frontend
pnpm run dev --host
```

### 6. 验证部署

访问以下地址验证服务是否正常运行：

- 前端应用: http://localhost:5173
- 后端 API: http://localhost:5050
- 健康检查: http://localhost:5050/api/career/health

## 测试环境部署

### 1. 构建生产版本

**构建前端：**
```bash
cd career_navigator_frontend
pnpm run build

# 验证构建结果
ls -la dist/
```

**准备后端：**
```bash
cd ../career_navigator_backend

# 复制前端构建文件到后端静态目录
cp -r ../career_navigator_frontend/dist/* src/static/

# 验证静态文件
ls -la src/static/
```

### 2. 配置测试环境

创建测试环境配置：

```bash
cat > config/test.py << EOF
import os

class TestConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'test-secret-key'
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = True
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/test.log'
    
    # CORS 配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
EOF
```

### 3. 启动测试服务

```bash
# 设置环境变量
export FLASK_ENV=testing
export DASHSCOPE_API_KEY="your_api_key_here"

# 启动服务
cd career_navigator_backend
source venv/bin/activate
python src/main.py
```

### 4. 运行测试

```bash
# 运行后端测试
python -m pytest tests/ -v

# 运行前端测试
cd ../career_navigator_frontend
pnpm test
```

## 生产环境部署

### 方案一：传统部署

#### 1. 服务器准备

```bash
# 创建应用用户
sudo useradd -m -s /bin/bash careernavigator
sudo usermod -aG sudo careernavigator

# 创建应用目录
sudo mkdir -p /opt/careernavigator
sudo chown careernavigator:careernavigator /opt/careernavigator

# 切换到应用用户
sudo su - careernavigator
```

#### 2. 部署应用

```bash
# 克隆代码到生产目录
cd /opt/careernavigator
git clone <repository-url> .

# 设置后端
cd career_navigator_backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 构建前端
cd ../career_navigator_frontend
pnpm install
pnpm run build

# 复制前端文件
cp -r dist/* ../career_navigator_backend/src/static/
```

#### 3. 配置生产环境

```bash
# 创建生产配置
cat > /opt/careernavigator/config/production.py << EOF
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///production.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    
    # 安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 日志配置
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/careernavigator/app.log'
    
    # CORS 配置
    CORS_ORIGINS = ['https://yourdomain.com']
EOF

# 创建环境变量文件
cat > /opt/careernavigator/.env << EOF
FLASK_ENV=production
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DASHSCOPE_API_KEY=your_production_api_key_here
DATABASE_URL=sqlite:///production.db
EOF

# 创建日志目录
sudo mkdir -p /var/log/careernavigator
sudo chown careernavigator:careernavigator /var/log/careernavigator
```

#### 4. 配置进程管理

**使用 systemd 服务：**

```bash
# 创建 systemd 服务文件
sudo cat > /etc/systemd/system/careernavigator.service << EOF
[Unit]
Description=CareerNavigator Flask Application
After=network.target

[Service]
Type=simple
User=careernavigator
Group=careernavigator
WorkingDirectory=/opt/careernavigator/career_navigator_backend
Environment=PATH=/opt/careernavigator/career_navigator_backend/venv/bin
EnvironmentFile=/opt/careernavigator/.env
ExecStart=/opt/careernavigator/career_navigator_backend/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable careernavigator
sudo systemctl start careernavigator

# 检查服务状态
sudo systemctl status careernavigator
```

#### 5. 配置反向代理

**使用 Nginx：**

```bash
# 安装 Nginx
sudo apt install nginx -y

# 创建站点配置
sudo cat > /etc/nginx/sites-available/careernavigator << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 重定向到 HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # 静态文件
    location /static/ {
        alias /opt/careernavigator/career_navigator_backend/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 前端应用
    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/careernavigator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 方案二：Docker 部署

#### 1. 创建 Dockerfile

**后端 Dockerfile：**
```dockerfile
# career_navigator_backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5050

# 启动命令
CMD ["python", "src/main.py"]
```

**前端构建 Dockerfile：**
```dockerfile
# career_navigator_frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN npm install -g pnpm && pnpm install

# 复制源代码
COPY . .

# 构建应用
RUN pnpm run build

# 使用 nginx 提供静态文件
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 2. 创建 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./career_navigator_backend
    ports:
      - "5050:5050"
    environment:
      - FLASK_ENV=production
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5050/api/career/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./career_navigator_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  logs:
  data:
```

#### 3. 部署命令

```bash
# 创建环境变量文件
cat > .env << EOF
DASHSCOPE_API_KEY=your_api_key_here
SECRET_KEY=$(openssl rand -hex 32)
EOF

# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 配置管理

### 环境变量配置

**必需的环境变量：**

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API 密钥 | `sk-xxx` |
| `SECRET_KEY` | Flask 应用密钥 | `random-secret-key` |
| `FLASK_ENV` | Flask 运行环境 | `production` |

**可选的环境变量：**

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///app.db` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_FILE` | 日志文件路径 | `logs/app.log` |
| `CORS_ORIGINS` | 允许的跨域来源 | `*` |

### 配置文件管理

**开发环境配置：**
```python
# config/development.py
class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    LOG_LEVEL = 'DEBUG'
```

**生产环境配置：**
```python
# config/production.py
class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    LOG_LEVEL = 'WARNING'
```

## 监控与维护

### 日志管理

**配置日志轮转：**
```bash
# 创建 logrotate 配置
sudo cat > /etc/logrotate.d/careernavigator << EOF
/var/log/careernavigator/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 careernavigator careernavigator
    postrotate
        systemctl reload careernavigator
    endscript
}
EOF
```

### 性能监控

**使用 Prometheus 和 Grafana：**

```yaml
# monitoring/docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

### 健康检查

**应用健康检查端点：**
```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }
```

**系统监控脚本：**
```bash
#!/bin/bash
# monitor.sh

# 检查服务状态
if ! systemctl is-active --quiet careernavigator; then
    echo "CareerNavigator service is down, restarting..."
    systemctl restart careernavigator
fi

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is high: ${DISK_USAGE}%"
fi

# 检查内存使用
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "Memory usage is high: ${MEMORY_USAGE}%"
fi
```

### 备份策略

**数据库备份：**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups/careernavigator"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/careernavigator/career_navigator_backend/src/database/app.db \
   $BACKUP_DIR/app_${DATE}.db

# 备份配置文件
tar -czf $BACKUP_DIR/config_${DATE}.tar.gz \
    /opt/careernavigator/.env \
    /opt/careernavigator/config/

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## 故障排除

### 常见问题

#### 1. API 密钥错误

**症状：** 后端启动失败，提示 API 密钥无效

**解决方案：**
```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY

# 验证 API 密钥
curl -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
     https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
```

#### 2. 前端构建失败

**症状：** `pnpm run build` 命令失败

**解决方案：**
```bash
# 清理缓存
pnpm store prune

# 重新安装依赖
rm -rf node_modules pnpm-lock.yaml
pnpm install

# 检查 Node.js 版本
node --version  # 应该是 20.x
```

#### 3. 数据库连接问题

**症状：** 应用启动时数据库连接失败

**解决方案：**
```bash
# 检查数据库文件权限
ls -la src/database/

# 重新创建数据库
rm src/database/app.db
python -c "from src.models.user import db; db.create_all()"
```

#### 4. 内存不足

**症状：** 应用运行缓慢或崩溃

**解决方案：**
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 重启服务
systemctl restart careernavigator

# 考虑增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 调试技巧

**启用调试模式：**
```bash
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
python src/main.py
```

**查看详细日志：**
```bash
# 实时查看日志
tail -f /var/log/careernavigator/app.log

# 搜索错误
grep -i error /var/log/careernavigator/app.log
```

**性能分析：**
```bash
# 使用 htop 监控系统资源
htop

# 使用 iotop 监控磁盘 I/O
sudo iotop

# 使用 netstat 检查网络连接
netstat -tulpn | grep :5050
```

## 安全建议

### 1. 网络安全

- 使用 HTTPS 加密传输
- 配置防火墙规则
- 定期更新 SSL 证书
- 启用 HSTS 头

### 2. 应用安全

- 定期更新依赖包
- 使用强密码和密钥
- 限制 API 访问频率
- 验证用户输入

### 3. 系统安全

- 定期更新操作系统
- 配置自动安全更新
- 监控异常访问
- 备份重要数据

### 4. 数据安全

- 加密敏感数据
- 定期备份数据
- 限制数据访问权限
- 遵守数据保护法规

---

通过遵循本部署指南，您可以成功地在各种环境中部署 CareerNavigator 系统。如果遇到问题，请参考故障排除部分或联系技术支持。

