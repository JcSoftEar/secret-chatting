# Secret Chatting

一个基于 Flask + SocketIO 的加密聊天室应用，支持匿名聊天和管理员后台监控。

[English](README_EN.md)

## 项目简介

Secret Chatting 是一个轻量级的私密聊天室系统。用户通过房间号和密码加入聊天室，支持自定义昵称，所有消息实时传输并持久化存储。管理员可通过后台监控所有房间的聊天记录、创建和删除房间，并可直接在房间内发送管理消息。系统首次使用时提供可视化初始化向导，自动完成数据库创建和管理员设置。前端采用仿微信风格设计，体验流畅自然。

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
    ├── admin.html      # 管理端页面
    └── setup.html      # 系统初始化页面
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

### 3. 系统初始化

首次启动时，访问任意页面会自动跳转到初始化页面（`/setup`），需完成以下步骤：

1. **创建数据库** — 自动创建 SQLite 数据库文件
2. **初始化数据表** — 自动创建 Room、Message、Admin 三张表
3. **创建管理员** — 设置管理员账号和密码（密码不少于6位）

初始化完成后自动跳转到管理后台登录页。

> 系统已初始化后，访问 `/setup` 会自动跳转到管理后台。

### 4. 访问页面

| 页面 | 地址 | 说明 |
|------|------|------|
| 聊天室 | http://localhost:5000 | 用户聊天入口 |
| 系统初始化 | http://localhost:5000/setup | 首次使用时自动跳转 |
| 管理后台 | http://localhost:5000/admin | 管理员登录后管理房间 |

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
