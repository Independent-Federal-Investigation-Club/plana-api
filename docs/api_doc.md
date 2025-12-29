### 📑 Guild API Reference

## Guild Data Model

The `Guild` model represents Discord server information with all associated data like users, roles, channels, etc.

### Guild Structure
```json
{
  "id": 123456789012345678,
  "name": "My Awesome Discord Server",
  "icon": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "banner": "z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4",
  "owner_id": 987654321098765432,
  "premium_tier": 2,
  "premium_subscription_count": 15,
  "users": [
    {
      "user_id": 111222333444555666,
      "username": "john_doe",
      "avatar": "abc123def456ghi789jkl012mno345pq"
    }
  ],
  "roles": [
    {
      "role_id": 777888999000111222,
      "name": "Admin",
      "color": 16711680,
      "permissions": 8,
      "position": 5
    }
  ],
  "emojis": [
    {
      "emoji_id": 333444555666777888,
      "name": "custom_emoji",
      "url": "https://cdn.discordapp.com/emojis/333444555666777888.png",
      "animated": false
    }
  ],
  "stickers": [
    {
      "sticker_id": 444555666777888999,
      "name": "cool_sticker",
      "url": "https://cdn.discordapp.com/stickers/444555666777888999.png",
      "description": "A really cool sticker",
      "emoji": "😎",
      "format": 1,
      "available": true
    }
  ],
  "channels": [
    {
      "channel_id": 555666777888999000,
      "name": "general",
      "type": 0,
      "position": 1,
      "topic": "General discussion channel",
      "nsfw": false
    }
  ],
  "categories": [
    {
      "channel_id": 666777888999000111,
      "name": "COMMUNITY",
      "type": 4,
      "position": 0,
      "topic": null,
      "nsfw": false
    }
  ]
}
```

### Guild Field Descriptions

**Core Fields:**
- `id`: Discord server snowflake ID (required)
- `name`: Server name (max 100 characters)
- `icon`: Server icon hash (32 characters)
- `banner`: Server banner hash (32 characters) 
- `owner_id`: Discord user ID of server owner
- `premium_tier`: Nitro boost level (0=None, 1=Tier 1, 2=Tier 2, 3=Tier 3)
- `premium_subscription_count`: Number of Nitro boosts

**User Objects:**
- `user_id`: Discord user snowflake ID
- `username`: Discord username (max 100 chars)
- `avatar`: User avatar hash (32 chars)

**Role Objects:**
- `role_id`: Discord role snowflake ID
- `name`: Role name (max 100 chars)
- `color`: Role color in decimal format (RGB converted to integer)
- `permissions`: Permission bitfield as integer
- `position`: Role hierarchy position

**Channel Objects:**
- `channel_id`: Discord channel snowflake ID
- `name`: Channel name (max 100 chars)
- `type`: Channel type (0=Text, 2=Voice, 4=Category, 5=News, etc.)
- `position`: Channel position in list
- `topic`: Channel topic/description (max 1024 chars)
- `nsfw`: Whether channel is age-restricted

**Emoji Objects:**
- `emoji_id`: Discord emoji snowflake ID
- `name`: Emoji name (max 100 chars)
- `url`: Direct URL to emoji image
- `animated`: Whether emoji is animated GIF

**Sticker Objects:**
- `sticker_id`: Discord sticker snowflake ID
- `name`: Sticker name (max 100 chars)
- `description`: Sticker description (max 512 chars)
- `emoji`: Associated emoji character
- `format`: Format type (1=PNG, 2=APNG, 3=LOTTIE, 4=GIF)
- `available`: Whether sticker is available for use

## AI Configuration Data Model

The `AI` model defines the configuration for AI-assisted features within a guild, including personality, memory scope, and engagement behavior.

### AI Configuration Structure
```json
{
  "enabled": true,
  "stream": true,
  "engage_mode": false,
  "engage_rate": 0.05,
  "memory_type": 1,
  "memory_limit": 50,
  "system_prompt": "You are Plana, a helpful assistant...",
  "input_template": "{user.mention} asks: \"{message.content}\"",
  "target_roles": [123456789012345678],
  "target_roles_mode": true,
  "target_channels": [987654321098765432],
  "target_channels_mode": false,
  "ai_moderation": false,
  "reaction_responses": true
}
```

### AI Field Descriptions

- `enabled`: Whether AI features are enabled for the guild.
- `stream`: Enable streaming responses from the AI.
- `engage_mode`: Engagement mode: `false` for passive (only mentioned), `true` for active (responds to messages).
- `engage_rate`: Probability (0.0 to 1.0) of AI engaging when in active mode.
- `memory_type`: Memory scope: `1` (guild-wide), `2` (per-category), `3` (per-channel).
- `memory_limit`: Maximum number of messages to include in the context.
- `system_prompt`: Custom system prompt to define AI personality.
- `input_template`: Template for formatting user input to the AI.
- `target_roles`: List of role IDs to include/exclude.
- `target_roles_mode`: `false` for blacklist (ignore roles), `true` for whitelist (allow only these roles).
- `target_channels`: List of channel IDs to include/exclude.
- `target_channels_mode`: `false` for blacklist (ignore channels), `true` for whitelist (allow only these channels).
- `ai_moderation`: Enable AI-assisted moderation features.
- `reaction_responses`: Allow the AI to respond using Discord reactions.

## Message Data Model

The `Message` model is a core data structure used across multiple endpoints for creating rich Discord messages with embeds, components, and reactions.

### Message Structure
```json
{
  "id": 1234567890,
  "message_id": 555666777,
  "guild_id": 123456789,
  "channel_id": 987654321,
  "content": "Hello world!",
  "embeds": [
    {
      "title": "Example Embed",
      "description": "This is an example embed",
      "color": 7506394,
      "footer": {
        "text": "Footer text",
        "icon_url": "https://example.com/icon.png"
      },
      "author": {
        "name": "Author Name",
        "url": "https://example.com",
        "icon_url": "https://example.com/author.png"
      },
      "fields": [
        {
          "name": "Field Name",
          "value": "Field Value",
          "inline": true
        }
      ],
      "image": "https://example.com/image.png",
      "thumbnail": "https://example.com/thumb.png",
      "timestamp": "2024-01-01T12:00:00Z",
      "url": "https://example.com"
    }
  ],
  "components": [
    {
      "custom_id": "button_1",
      "label": "Click Me",
      "style": 1,
      "emoji": {
        "name": "🎮",
        "id": null,
        "animated": false
      },
      "disabled": false
    },
    {
      "custom_id": "select_menu",
      "placeholder": "Choose an option",
      "min_values": 1,
      "max_values": 1,
      "options": [
        {
          "label": "Option 1",
          "value": "opt1",
          "description": "First option",
          "emoji": {
            "name": "1️⃣",
            "id": null,
            "animated": false
          },
          "default": false
        }
      ],
      "disabled": false
    }
  ],
  "reactions": [
    {
      "name": "👍",
      "id": null,
      "animated": false
    }
  ],
  "published": true,
  "updated_at": "2024-01-01T12:00:00"
}
```

### Component Types

**Button Component:**
- `custom_id`: Custom identifier (max 100 chars) OR `url` for link buttons
- `label`: Button text (max 80 chars)
- `style`: Button style (1=Primary, 2=Secondary, 3=Success, 4=Danger, 5=Link)
- `emoji`: Optional emoji
- `disabled`: Whether button is disabled

**Select Menu Component:**
- `custom_id`: Custom identifier (max 100 chars)
- `placeholder`: Placeholder text (max 150 chars)
- `min_values`/`max_values`: Selection limits (0-25)
- `options`: Array of select options
- `disabled`: Whether menu is disabled

**Embed Limits:**
- Title: 256 characters
- Description: 2048 characters
- Fields: Max 25 per embed
- Field name: 256 characters
- Field value: 1024 characters
- Footer text: 2048 characters

#### Guild Core Management _(Uses Guild Model)_

- **GET `/api/guilds/{guild_id}/data`**
  - _Description_: Get complete guild data including users, roles, channels, emojis, and stickers
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "id": 123456789012345678,
      "name": "My Discord Server",
      "icon": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
      "banner": "z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4",
      "owner_id": 987654321098765432,
      "premium_tier": 2,
      "premium_subscription_count": 5,
      "users": [
        {
          "user_id": 111222333444555666,
          "username": "john_doe",
          "avatar": "abc123def456ghi789"
        }
      ],
      "roles": [
        {
          "role_id": 777888999000111222,
          "name": "Admin",
          "color": 16711680,
          "permissions": 8,
          "position": 5
        }
      ],
      "emojis": [
        {
          "emoji_id": 333444555666777888,
          "name": "custom_emoji",
          "url": "https://cdn.discordapp.com/emojis/333444555666777888.png",
          "animated": false
        }
      ],
      "stickers": [],
      "channels": [
        {
          "channel_id": 555666777888999000,
          "name": "general",
          "type": 0,
          "position": 1,
          "topic": "General discussion",
          "nsfw": false
        }
      ],
      "categories": [
        {
          "channel_id": 666777888999000111,
          "name": "COMMUNITY",
          "type": 4,
          "position": 0,
          "topic": null,
          "nsfw": false
        }
      ]
    }
    ```

- **POST `/api/guilds/{guild_id}/data`** _(Bot Only)_
  - _Description_: Create a new guild entry in the database (used when bot joins a server)
  - _Headers_: `Authorization: Bearer <bot_token>`, `Content-Type: application/json`
  - _Payload_:
    ```json
    {
      "id": 123456789012345678,
      "name": "My Discord Server",
      "icon": "a1b2c3d4e5f6g7h8i9j0",
      "banner": "z9y8x7w6v5u4t3s2r1q0",
      "owner_id": 987654321098765432,
      "premium_tier": 0,
      "premium_subscription_count": 0,
      "users": [],
      "roles": [
        {
          "role_id": 123456789012345678,
          "name": "@everyone",
          "color": 0,
          "permissions": 104324673,
          "position": 0
        }
      ],
      "channels": [],
      "emojis": [],
      "stickers": [],
      "categories": []
    }
    ```
  - _Sample Response_: (same as GET guild)

- **PUT/PATCH `/api/guilds/{guild_id}/data`** _(Bot Only)_
  - _Description_: Update guild data (used when guild information changes)
  - _Headers_: `Authorization: Bearer <bot_token>`, `Content-Type: application/json`
  - _Payload_: (same as POST - any fields can be updated)
  - _Sample Response_: (same as GET guild)

- **DELETE `/api/guilds/{guild_id}/data`** _(Bot Only)_
  - _Description_: Delete guild data (used when bot leaves a server)
  - _Headers_: `Authorization: Bearer <bot_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "Guild deleted successfully" }
    ```

#### Guild Preferences

- **GET `/api/guilds/{guild_id}/preferences`**
  - _Description_: Get guild preferences
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "guild_id": 123456789,
      "enabled": true,
      "command_prefix": "!",
      "language": "en-US",
      "timezone": "UTC",
      "embed_color": "#7289DA",
      "embed_footer": "Project Plana, Powered by S.C.H.A.L.E.",
      "embed_footer_images": []
    }
    ```

- **POST `/api/guilds/{guild_id}/preferences`**
  - _Description_: Create guild preferences
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_:
    ```json
    {
      "enabled": true,
      "command_prefix": "!",
      "language": "en-US",
      "timezone": "UTC",
      "embed_color": "#7289DA",
      "embed_footer": "Project Plana"
    }
    ```
  - _Sample Response_: (same as GET preferences)

- **PUT/PATCH `/api/guilds/{guild_id}/preferences`**
  - _Description_: Update guild preferences
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_: (same as POST)
  - _Sample Response_: (same as GET preferences)

- **DELETE `/api/guilds/{guild_id}/preferences`**
  - _Description_: Delete guild preferences
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "Guild preferences deleted successfully" }
    ```

#### Guild Messages _(Uses Message Model)_

- **GET `/api/guilds/{guild_id}/messages`**
  - _Description_: List guild messages with pagination
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Query Parameters_: `limit` (max 100, default 50), `offset` (default 0)
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "data": [
        {
          "id": 1234567890,
          "guild_id": 123456789,
          "channel_id": 987654321,
          "message_id": 555666777,
          "content": "Hello world!",
          "embeds": [],
          "components": [],
          "reactions": [],
          "published": true,
          "updated_at": "2024-01-01T12:00:00"
        }
      ],
      "total": 25
    }
    ```

- **GET `/api/guilds/{guild_id}/messages/{message_id}`**
  - _Description_: Get a specific message
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_: (single message object from Message model)

- **POST `/api/guilds/{guild_id}/messages`**
  - _Description_: Create a new message
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_: (Message model structure - see Message Data Model above)
  - _Sample Response_: (created message object)

- **PUT/PATCH `/api/guilds/{guild_id}/messages/{message_id}`**
  - _Description_: Update a specific message
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_: (Message model structure)
  - _Sample Response_: (updated message object)

- **DELETE `/api/guilds/{guild_id}/messages/{message_id}`**
  - _Description_: Delete a specific message
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "Message deleted successfully" }
    ```

#### Guild Users

- **GET `/api/guilds/{guild_id}/users`**
  - _Description_: List guild users with pagination
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Query Parameters_: `limit` (max 100, default 50), `offset` (default 0)
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "data": [
        {
          "id": 1234567890,
          "user_id": 987654321,
          "guild_id": 123456789,
          "user_data": {},
          "updated_at": "2024-01-01T12:00:00"
        }
      ],
      "total": 150
    }
    ```

#### Guild React Roles

- **GET `/api/guilds/{guild_id}/react-roles`**
  - _Description_: List guild react roles with pagination
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Query Parameters_: `limit` (max 100, default 50), `offset` (default 0)
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "data": [
        {
          "id": 1234567890,
          "guild_id": 123456789,
          "message_id": 555666777,
          "name": "Role Selection",
          "role_assignments": [
            {
              "role_ids": [888999000, 888999001],
              "trigger_id": "🎮"
            }
          ],
          "enabled": true,
          "updated_at": "2024-01-01T12:00:00"
        }
      ],
      "total_count": 5
    }
    ```

- **POST `/api/guilds/{guild_id}/react-roles`**
  - _Description_: Create react role configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_:
    ```json
    {
      "message_id": 555666777,
      "name": "Role Selection",
      "role_assignments": [
        {
          "role_ids": [888999000, 111222333],
          "trigger_id": "🎮"
        }
      ],
      "enabled": true
    }
    ```
  - _Sample Response_: (same structure as GET single react role)

#### Guild Welcome System _(Uses Message Model)_

- **GET `/api/guilds/{guild_id}/welcome`**
  - _Description_: Get guild welcome configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "guild_id": 123456789,
      "enabled": true,
      "welcome_channel_id": 987654321,
      "goodbye_channel_id": 987654322,
      "dm_new_users": false,
      "welcome_message": {
        "content": "Welcome {user.mention}!",
        "embeds": [
          {
            "title": "Welcome!",
            "description": "Thanks for joining our server!",
            "color": 7506394
          }
        ],
        "components": []
      },
      "goodbye_message": null,
      "dm_message": null,
      "auto_roles": [888999000]
    }
    ```

- **POST `/api/guilds/{guild_id}/welcome`**
  - _Description_: Create welcome configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_:
    ```json
    {
      "enabled": true,
      "welcome_channel_id": 987654321,
      "dm_new_users": false,
      "welcome_message": {
        "content": "Welcome {user.mention}!",
        "embeds": [
          {
            "title": "Welcome!",
            "description": "Thanks for joining!",
            "color": 7506394
          }
        ]
      },
      "auto_roles": [888999000]
    }
    ```
  - _Sample Response_: (same as GET welcome)

- **PUT/PATCH `/api/guilds/{guild_id}/welcome`**
  - _Description_: Update welcome configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_: (same as POST)
  - _Sample Response_: (same as GET welcome)

- **DELETE `/api/guilds/{guild_id}/welcome`**
  - _Description_: Delete welcome configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "Welcome configuration deleted successfully" }
    ```

#### Guild Level System _(Uses Message Model)_

- **GET `/api/guilds/{guild_id}/levels`**
  - _Description_: Get guild level configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "guild_id": 123456789,
      "enabled": true,
      "announcement_type": "current_channel",
      "announcement_channel_id": null,
      "level_up_message": {
        "content": "Congratulations {user.mention}! You reached level {level}!",
        "embeds": [
          {
            "title": "Level Up!",
            "description": "You've reached level {level}!",
            "color": 7506394
          }
        ]
      },
      "xp_per_message": 15,
      "xp_cooldown_seconds": 60,
      "role_rewards": [
        {
          "level": 5,
          "role_id": 888999000,
          "remove_previous": false,
          "description": "Level 5 Reward"
        }
      ],
      "xp_boosters": [],
      "channel_mode": "blacklist",
      "channel_list": []
    }
    ```

- **POST `/api/guilds/{guild_id}/levels`**
  - _Description_: Create level system configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_:
    ```json
    {
      "enabled": true,
      "announcement_type": "current_channel",
      "level_up_message": {
        "content": "Congratulations {user.mention}! You reached level {level}!",
        "embeds": [
          {
            "title": "Level Up!",
            "color": 7506394
          }
        ]
      },
      "xp_per_message": 15,
      "xp_cooldown_seconds": 60,
      "role_rewards": [
        {
          "level": 5,
          "role_id": 888999000,
          "remove_previous": false
        }
      ]
    }
    ```
  - _Sample Response_: (same as GET levels)

- **PUT/PATCH `/api/guilds/{guild_id}/levels`**
  - _Description_: Update level system configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_: (same as POST)
  - _Sample Response_: (same as GET levels)

- **DELETE `/api/guilds/{guild_id}/levels`**
  - _Description_: Delete level system configuration
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "Level configuration deleted successfully" }
    ```

#### Guild RSS Feeds

- **GET `/api/guilds/{guild_id}/rss`**
  - _Description_: List all RSS feeds for a guild with pagination
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Query Parameters_: `limit` (max 100, default 50), `offset` (default 0)
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "data": [
        {
          "id": 1234567890,
          "guild_id": 123456789,
          "channel_id": 987654321,
          "url": "https://example.com/feed.xml",
          "name": "Example Feed",
          "enabled": true,
          "message": "New article: {title} - {link}",
          "last_updated": "2024-01-01T12:00:00"
        }
      ],
      "total_count": 3
    }
    ```

- **POST `/api/guilds/{guild_id}/rss`**
  - _Description_: Create a new RSS feed for the guild
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_:
    ```json
    {
      "channel_id": 987654321,
      "url": "https://example.com/feed.xml",
      "name": "Example Feed",
      "enabled": true,
      "message": "New article: {title} - {link}"
    }
    ```
  - _Sample Response_: (single RSS feed object)

- **GET `/api/guilds/{guild_id}/rss/{rss_id}`**
  - _Description_: Get a specific RSS feed for the guild
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    {
      "id": 1234567890,
      "guild_id": 123456789,
      "channel_id": 987654321,
      "url": "https://example.com/feed.xml",
      "name": "Example Feed",
      "enabled": true,
      "message": "New article: {title} - {link}",
      "last_updated": "2024-01-01T12:00:00"
    }
    ```

- **PUT/PATCH `/api/guilds/{guild_id}/rss/{rss_id}`**
  - _Description_: Update a specific RSS feed
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_:
    ```json
    {
      "channel_id": 987654321,
      "url": "https://example.com/feed.xml",
      "name": "Updated Feed Name",
      "enabled": false,
      "message": "Updated message: {title}"
    }
    ```
  - _Sample Response_: (updated RSS feed object)

- **DELETE `/api/guilds/{guild_id}/rss/{rss_id}`**
  - _Description_: Delete a specific RSS feed
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "RSS feed deleted successfully" }
    ```

**RSS Feed Message Template Variables:**
- `{title}`: Article title
- `{link}`: Article URL
- `{description}`: Article description/summary
- `{author}`: Article author
- `{pubDate}`: Publication date (full format)
- `{pubDateShort}`: Publication date (short format)
- `{pubDateTime}`: Publication date with time
- `{pubDateISO}`: Publication date in ISO format
- `{categories}`: Article categories
- `{feedName}`: RSS feed name
- `{feedUrl}`: RSS feed URL

#### Guild Images

- **POST `/api/guilds/{guild_id}/images`**
  - _Description_: Upload an image file for a specific guild
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: multipart/form-data`
  - _Form Data_:
    - `file`: Image file (JPG, PNG, GIF, WebP) - Max size: 10MB
  - _Sample Response_:
    ```json
    {
      "success": true,
      "message": "Image uploaded successfully",
      "data": {
        "url": "https://s3.amazonaws.com/bucket/guild_123456789/image_abc123.jpg",
        "guild_id": 123456789,
        "filename": "my_image.jpg",
        "content_type": "image/jpeg"
      }
    }
    ```
  - _Error Responses_:
    - `400`: No file provided or invalid file type
    - `413`: File too large (exceeds 10MB limit)
    - `500`: Upload failed or internal server error

#### Guild AI Configuration

- **GET `/api/guilds/{guild_id}/ai`**
  - _Description_: Get the AI configuration for a guild.
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_: (single AI configuration object)

- **POST `/api/guilds/{guild_id}/ai`**
  - _Description_: Create an AI configuration for a guild.
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_: (AI configuration structure - see AI Configuration Data Model above)
  - _Sample Response_: (created AI configuration object)

- **PUT/PATCH `/api/guilds/{guild_id}/ai`**
  - _Description_: Update the AI configuration for a guild.
  - _Headers_: `Authorization: Bearer <jwt_token>`, `Content-Type: application/json`
  - _Payload_: (AI configuration structure)
  - _Sample Response_: (updated AI configuration object)

- **DELETE `/api/guilds/{guild_id}/ai`**
  - _Description_: Delete the AI configuration for a guild.
  - _Headers_: `Authorization: Bearer <jwt_token>`
  - _Payload_: None
  - _Sample Response_:
    ```json
    { "message": "AI configuration deleted successfully" }
    ```

#### Notes

- All endpoints require proper JWT authentication via `Authorization: Bearer <token>` header
- Bot-only endpoints require bot-level authentication
- Guild IDs should be valid Discord snowflake IDs (18-19 digit integers)
- Paginated endpoints support `limit` (max 100) and `offset` query parameters
- All timestamps are in UTC format
- Color values must be valid hex colors (e.g., "#7289DA")
- **Guild Model** contains complete Discord server information with users, roles, channels, etc.
- **AI Model** is used for configuring guild-specific AI behavior and memory.
- **Message Model** is used in: `/messages`, `/welcome`, `/levels` endpoints
- Message components support buttons and select menus with full Discord API compatibility
- Embed color values are integers (convert hex to decimal: `#7289DA` = `7506394`)
- Variable placeholders like `{user.mention}`, `{level}`, `{title}` are supported in message content