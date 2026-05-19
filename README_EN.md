# Secret Chatting

A secure chat room application built with Flask + SocketIO, featuring anonymous chat and admin dashboard monitoring.

[中文文档](README.md)

## Introduction

Secret Chatting is a lightweight private chat room system. Users join chat rooms with a room ID and password, with support for custom nicknames. All messages are transmitted in real-time and persistently stored. Administrators can monitor all room chat histories, create and delete rooms, and send messages directly within rooms through the admin dashboard. The system provides a visual setup wizard on first use, automatically completing database creation and admin setup. The frontend features a WeChat-inspired design for a smooth and natural experience.

## Features

- **Anonymous Chat**: Join chat rooms with room ID and password, support custom nicknames or auto-generated ones
- **Real-time Communication**: WebSocket-based instant message delivery
- **Admin Dashboard**: View all rooms, monitor chat history, create/delete rooms, send admin messages
- **Message Persistence**: All chat records are saved to the database, view history when rejoining a room
- **WeChat-style UI**: Both client and admin interfaces adopt WeChat-inspired visual design

## Tech Stack

- **Backend**: Flask + Flask-SQLAlchemy + Flask-SocketIO
- **Frontend**: Vanilla HTML/CSS/JS + Socket.IO Client
- **Database**: SQLite (configurable to other databases)

## Project Structure

```
secret-chatting/
├── app.py              # Application entry
├── config.py           # Configuration management
├── extensions.py       # Flask extension instances (db, socketio)
├── models.py           # Data models (Room, Message, Admin)
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── routes/             # Route blueprints
│   ├── main.py         # Home, setup and general routes
│   └── admin.py        # Admin API routes
├── sockets/            # SocketIO event handlers
│   ├── chat.py         # User chat events (join, send_msg)
│   └── admin.py        # Admin events (admin_connect, admin_join)
├── utils/              # Utility functions
│   └── __init__.py     # DB initialization check, etc.
├── static/
│   ├── css/
│   │   ├── style.css   # Client styles
│   │   └── admin.css   # Admin styles
│   └── js/
│       ├── app.js      # Client logic
│       └── admin.js    # Admin logic
└── templates/
    ├── index.html      # Client page
    ├── admin.html      # Admin page
    └── setup.html      # System initialization page
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python app.py
```

### 3. System Initialization

On first launch, visiting any page will automatically redirect to the setup page (`/setup`). Complete the following steps:

1. **Create Database** — Automatically creates the SQLite database file
2. **Initialize Tables** — Automatically creates Room, Message, and Admin tables
3. **Create Admin** — Set up admin username and password (minimum 6 characters)

After initialization, you'll be redirected to the admin login page.

> Once the system is initialized, visiting `/setup` will redirect to the admin dashboard.

### 4. Access Pages

| Page | URL | Description |
|------|-----|-------------|
| Chat Room | http://localhost:5000 | User chat entry |
| System Setup | http://localhost:5000/setup | Auto-redirect on first use |
| Admin Dashboard | http://localhost:5000/admin | Admin login & room management |

## Configuration

Configure via `.env` file or environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key | dev-secret-key-change-this-in-production |
| DATABASE_URL | Database connection string | sqlite:///secret_chatting.db |

## Data Models

- **Room**: Chat room (room_id, password, name)
- **Message**: Chat message (room_id, sender_name, content, timestamp)
- **Admin**: Administrator (username, password_hash)

## License

[MIT](LICENSE)
