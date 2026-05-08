# Secret Chatting

一个基于 Flask + SocketIO 的加密聊天室应用，支持匿名聊天和管理员后台监控。

## 功能特性

- **匿名聊天**：用户可通过房间号和密码加入聊天室，支持自定义昵称或随机生成
- **实时通信**：基于 WebSocket 的实时消息推送
- **管理后台**：管理员可查看所有房间、监控聊天记录、创建/删除房间、发送管理消息
- **消息持久化**：所有聊天记录保存到数据库，重新进入房间可查看历史消息
- **仿微信 UI**：客户端和管理端均采用仿微信视觉风格

## 技术栈

- **后端**：Flask + Flask-SQLAlchemy + Flask-SocketIO
- **前端**：原生 HTML/CSS/JS + Socket.IO Client
- **数据库**：SQLite（可切换其他数据库）

## 项目结构

```
secret-chatting/
├── app.py              # 应用入口，路由与 SocketIO 事件
├── config.py           # 配置管理
├── models.py           # 数据模型（Room, Message, Admin）
├── init_db.py          # 数据库初始化脚本
├── requirements.txt    # Python 依赖
├── .env                # 环境变量
├── static/
│   ├── css/
│   │   ├── style.css   # 客户端样式
│   │   └── admin.css   # 管理端样式
│   └── js/
│       ├── app.js      # 客户端逻辑
│       └── admin.js    # 管理端逻辑
└── templates/
    ├── index.html      # 客户端页面
    └── admin.html      # 管理端页面
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

默认创建：
- 测试房间：`room123` / `password123`
- 管理员账号：`admin` / `admin123`

### 3. 启动服务

```bash
python app.py
```

### 4. 访问页面

| 页面 | 地址 |
|------|------|
| 聊天室 | http://localhost:5000 |
| 管理后台 | http://localhost:5000/admin |

## 配置说明

通过 `.env` 文件或环境变量配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| SECRET_KEY | Flask 密钥 | dev-secret-key-change-this-in-production |
| DATABASE_URL | 数据库连接字符串 | sqlite:///secret_chatting.db |

## 数据模型

- **Room**：聊天房间（room_id, password, name）
- **Message**：聊天消息（room_id, sender_name, content, timestamp）
- **Admin**：管理员（username, password_hash）

## License

[MIT](LICENSE)
