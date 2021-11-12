# social-network

## Setup
### Development
1. rename `.env.dev-sample` to `.env.dev`
2. update .env files and `docker-compose.yml` if you want
2. run `docker-compose up --build`

### Production
1. rename `.env.prod-sample` and `.env.prod.db-sample` to `.env.prod` and `.env.prod.db`
2. update .env files and `docker-compose.prod.yml` if you want
2. run `docker-compose -f docker-compose.prod.yml up --build`

### Enums
#### Notification
| ID | Name | Description |
| :---- | ---- | ----: |
| 1 | Chat message | New unread message |
| 2 | Friend request | New friend request |

#### Chat
| ID | Name | Description |
| :---- | ---- | ----: |
| 1 | Common | Chat with any users amount |
| 2 | Direct(only 2 users) | Chat only between 2 users |

#### Membership
| ID | Name | Description |
| :---- | ---- | ----: |
| 1 | Admin | |
| 2 | Regular | |
