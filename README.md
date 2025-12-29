# Plana Discord Bot API

A modern, production-ready FastAPI backend for Discord bot management with OAuth 2.0 authentication and comprehensive guild management features.

## ✨ Features

- **🔐 Discord OAuth 2.0 Authentication**: Secure user authentication using Discord's OAuth 2.0 flow
- **🛡️ Advanced Permission System**: Checks Discord admin permissions and custom additional admin roles
- **⚙️ Guild Management**: Full CRUD operations for guild preferences and settings
- **🔑 JWT Token Authentication**: Secure API access with JWT tokens and proper validation
- **🗄️ Database Integration**: PostgreSQL integration using SQLAlchemy with async support
- **🔒 Middleware Protection**: Route-level authentication and authorization
- **📊 Comprehensive Logging**: Structured logging with loguru and file rotation
- **✅ Input Validation**: Pydantic models with comprehensive validation
- **🚀 Production Ready**: Proper error handling, CORS configuration, and security measures

## 🏗️ Architecture

The API follows clean architecture principles with:
- **Routes**: API endpoints organized by functionality
- **Middleware**: Authentication and request processing
- **Models**: Database models with enhanced operations
- **Services**: Business logic separation
- **Validation**: Input validation and error handling

## 📚 API Endpoints

### Authentication Endpoints

- `GET /api/auth/url` - Get Discord OAuth authorization URL
- `GET /api/auth/callback` - Handle OAuth callback, exchange code for JWT token, and redirect to frontend
- `GET /api/auth/me` - Get current authenticated user information
- `POST /api/auth/logout` - Logout user (client-side token removal)
- `GET /api/auth/guilds` - Get user's Discord guilds with admin permissions

### Guild Management Endpoints

- `GET /api/guild/{guild_id}/preferences` - Get guild preferences
- `PUT /api/guild/{guild_id}/preferences` - Update guild preferences
- `DELETE /api/guild/{guild_id}/preferences` - Reset guild preferences to defaults

## 🔧 Setup and Installation

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Discord Application with OAuth 2.0 setup

### Quick Start

1. **Clone and navigate to the API directory**:
```bash
cd /path/to/Plana/api
```

2. **Install dependencies**:
```bash
# Using pip
pip install -r requirements.txt

# Or using the project's pyproject.toml
pip install -e ..
```

3. **Set up environment variables**:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
nano .env
```

4. **Initialize the database**:
```bash
python -c "
import asyncio
from plana.database.utils.db import init_db, PlanaDB
from dotenv import load_dotenv
import os

async def setup():
    load_dotenv()
    db = init_db(os.getenv('DATABASE_URL'))
    await PlanaDB.create_all()
    print('Database initialized successfully!')

asyncio.run(setup())
"
```

5. **Run the server**:
```bash
# Using the main module
python -m api.main

# Or using the run script
python api/run.py

# Or using uvicorn directly
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌍 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL database connection string | Yes | - |
| `DISCORD_CLIENT_ID` | Discord OAuth application client ID | Yes | - |
| `DISCORD_CLIENT_SECRET` | Discord OAuth application client secret | Yes | - |
| `DISCORD_REDIRECT_URI` | OAuth callback URL | Yes | - |
| `JWT_SECRET` | Secret key for JWT token signing | Yes | - |
| `API_HOST` | API server host | No | `0.0.0.0` |
| `API_PORT` | API server port | No | `8000` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | No | `localhost:3000,localhost:8000` |
| `DEBUG` | Enable debug mode | No | `false` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

## 🔐 Discord OAuth Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to **OAuth2 → General**
4. Add your redirect URI (e.g., `http://localhost:8000/api/auth/callback`)
5. Copy the **Client ID** and **Client Secret**
6. Set the **Scopes**: `identify` and `guilds`

## 🚀 Usage Examples

### Authentication Flow

1. **Get OAuth URL**:
```bash
curl -X GET "http://localhost:8000/api/auth/url"
```

2. **User visits the OAuth URL and authorizes**

3. **Exchange code for JWT token**:
```bash
curl -X POST "http://localhost:8000/api/auth/callback" \
  -H "Content-Type: application/json" \
  -d '{"code": "received_oauth_code"}'
```

4. **Use JWT token for authenticated requests**:
```bash
curl -X GET "http://localhost:8000/api/guild/123456789/preferences" \
  -H "Authorization: Bearer your_jwt_token"
```

### Guild Management

```bash
# Get guild preferences
curl -X GET "http://localhost:8000/api/guild/123456789/preferences" \
  -H "Authorization: Bearer your_jwt_token"

# Update guild preferences
curl -X PUT "http://localhost:8000/api/guild/123456789/preferences" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "command_prefix": ">>",
    "language": "en-US",
    "timezone": "America/New_York",

    "embed_color": "#ff0000"
  }'

```

## 🛠️ Development

### Running in Development Mode

```bash
# Set DEBUG=true in .env file
echo "DEBUG=true" >> .env

# Run with auto-reload
python -m api.main
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Code Quality

The codebase follows the **Zen of Python** principles:
- **Simple is better than complex**
- **Explicit is better than implicit**
- **Readability counts**
- **Errors should never pass silently**

## 🔒 Security Features

- **JWT Token Validation**: Secure token-based authentication
- **Input Validation**: Comprehensive Pydantic model validation
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **Error Handling**: Structured error responses without sensitive data leakage
- **Environment Variable Validation**: Required configuration checks
- **Logging**: Comprehensive audit trails

## 📁 Project Structure

```
api/
├── __init__.py
├── main.py                 # FastAPI application and configuration
├── run.py                  # Simple startup script
├── routes/                 # API endpoints
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   └── guild.py           # Guild management routes
├── auth/                   # Authentication logic
│   ├── __init__.py
│   └── discord_oauth.py   # Discord OAuth implementation
├── middleware/             # Request middleware
│   ├── __init__.py
│   └── auth.py            # Authentication middleware
├── logs/                   # Log files (auto-created)
├── .env.example           # Environment configuration template
└── README.md              # This file
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/dbname`
   - Ensure PostgreSQL is running and accessible

2. **Discord OAuth Errors**:
   - Verify `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`
   - Check redirect URI matches exactly in Discord Developer Portal

3. **JWT Token Issues**:
   - Ensure `JWT_SECRET` is set and secure
   - Check token expiration (24 hours by default)

4. **Permission Denied**:
   - Verify user has Administrator permission in Discord server
   - Check if additional admin roles are configured correctly

### Logging

Logs are written to:
- **Console**: Colored, formatted output
- **File**: `logs/api.log` with rotation (10MB, 7 days retention)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style and patterns
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for the Discord community**

### 📑 Simple API Reference

#### Authentication Endpoints

- **GET `/api/auth/url`**
  - _Description_: Get Discord OAuth authorization URL
  - _Headers_: None
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "url": "https://discord.com/oauth2/authorize?...",
      "state": "random_state_string"
    }
    ```

- **GET `/api/auth/callback`**
  - _Description_: Handles the OAuth2 callback from Discord. 
  - _Headers_: None
  - _Payload_: Query parameters: `code`, `state`
  - _Behavior_: 
    - **Default**: Returns HTML page with JavaScript that posts message to parent window (popup flow)
  - _Popup Response_: Returns HTML with embedded JavaScript:
    ```html
    <!DOCTYPE html>
    <html>
    <head><title>Authentication Complete</title></head>
    <body>
      <script>
        const token = 'jwt_token_here';
        
        if (window.opener) {
          window.opener.postMessage({
            type: 'DISCORD_OAUTH_SUCCESS',
            token: token,
          }, 'https://your-frontend-domain.com');
          window.close();
        } 
      </script>
      <p>Authentication successful. This window should close automatically.</p>
    </body>
    </html>

    ```
  - _JWT Token Payload_:
    ```json
    {
      "user_id": "123456789",
      "username": "user#1234",
      "avatar": "avatar_hash",
      "discord_access_token": "discord_access_token_value",
      "iat": 1710000000,
      "exp": 1710086400
    }
    ```
    - `user_id`: Discord user ID
    - `username`: Discord username
    - `avatar`: Discord avatar hash
    - `discord_access_token`: The user's Discord access token
    - `iat`: Issued at (UNIX timestamp)
    - `exp`: Expiration (UNIX timestamp, 24 hours after `iat`)

- **GET `/api/auth/me`**
  - _Description_: Get current authenticated user info
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "user": {
        "id": "123456789",
        "username": "user#1234",
        "avatar": "avatar_hash"
      }
    }
    ```

- **POST `/api/auth/logout`**
  - _Description_: Logout user (client-side token removal)
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "Logged out successfully" }
    ```

- **GET `/api/auth/guilds`**
  - _Description_: Get user's Discord guilds with admin permissions
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "guilds": [
        {
          "id": "123456789",
          "name": "My Server",
          "icon": "icon_hash",
          "owner": true,
          "permissions": 8
        }
      ],
      "user_id": "123456789"
    }
    ```

#### Guild Management Endpoints

- **GET `/api/guild/{guild_id}/preferences`**
  - _Description_: Get guild preferences
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "guild_id": 123456789,
      "command_prefix": "!",
      "language": "en-US",
      "timezone": "UTC",
      "embed_color": "#7289DA",
      "embed_footer": "Project Plana, Powered by S.C.H.A.L.E."
    }
    ```

- **PUT `/api/guild/{guild_id}/preferences`**
  - _Description_: Update guild preferences
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_ (example):
    ```json
    {
      "command_prefix": "!",
      "language": "en-US",
      "timezone": "UTC",
      "embed_color": "#7289DA",
      "embed_footer": "Project Plana"
    }
    ```
  - _Sample Response_: (same as GET preferences)
    ```json
    {
      "guild_id": 123456789,
      "command_prefix": "!",
      "language": "en-US",
      "timezone": "UTC",
      "embed_color": "#7289DA",
      "embed_footer": "Project Plana, Powered by S.C.H.A.L.E."
    }
    ```

- **DELETE `/api/guild/{guild_id}/preferences`**
  - _Description_: Reset guild preferences to defaults
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "Guild preferences reset to defaults" }
    ```