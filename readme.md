# Social Networking API

This Django Rest Framework project provides APIs for a social networking application.

## Getting Started

To get started with this project, follow these steps:

1. Clone the repository:

```bash
git clone <repository_url>
```

2. Navigate to the project directory:

```bash
cd <project_directory>
```

3. Build and run the Docker container:

```bash
docker-compose up --build
```

The above command will build the Docker image using the provided Dockerfile and docker-compose.yml, and then start the application. It will run the migrations, generate users, and start the Django development server.

## API Endpoints

### User Authentication

#### Sign Up

- `POST /user/api/v1/signup/`
  - Description: Allows users to sign up with their email.
  - Request Body:
    ```json
    {
        "email": "user@example.com",
        "password": "password123",
        "name": "John Doe"
    }
    ```
  - Response:
    ```json
    {
        "success": true,
        "response": {
            "message": "Signup successfully Completed!"
        }
    }
    ```

#### Log In

- `POST /user/api/v1/login/`
  - Description: Allows users to log in with their email and password. 
  - Request Body:
    ```json
    {
        "email": "user@example.com",
        "password": "password123"
    }
    ```
  - Response:
    ```json
    {
        "success": true,
        "response": {
            "message": "Login successful"
        }
    }
    ```

### User Management

#### Search Users

- `GET /user/api/v1/search/?q=<search_query>`
  - Description: Search for users by email or name.
  - Parameters:
    - `q`: Search query
  - Response:
    ```json
    {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 3,
                "email": "user@example.com",
                "name": "user"
            },
            {
                "id": 2,
                "email": "user2@example.com",
                "name": "user 2"
            }
        ]
    }
    ```

#### Send Friend Request

- `POST /social/api/v1/friend-request/`
  - Description: Send a friend request to another user.
  - Request Body:
    ```json
    {
        "action": "send",
        "friend_id": "2"
    }
    ```
  - Response:
    ```json
    {
        "success": true,
        "response": {
            "message": "Friend request sent successfully!"
        }
    }
    ```

#### Accept Friend Request

- `POST /social/api/v1/friend-request/`
  - Description: Accept a friend request.
  - Request Body:
    ```json
    {
        "action": "accept",
        "friend_request_id": "1"
    }
    ```
  - Response:
    ```json
    {
        "success": true,
        "response": {
            "message": "Friend request accepted successfully"
        }
    }
    ```

#### Reject Friend Request

- `POST /social/api/v1/friend-request/`
  - Description: Reject a friend request.
  - Request Body:
    ```json
    {
        "action": "reject",
        "friend_request_id": "2"
    }
    ```
  - Response:
    ```json
    {
        "success": true,
        "response": {
            "message": "Friend request rejected successfully!"
        }
    }
    ```

#### List Friends

- `GET /social/api/v1/friends/`
  - Description: List all friends of the current user.
  - Response:
    ```json
    {
        "count": 0,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 2,
                "email": "anotheruser@example.com",
                "name": "Jane Smith"
            }
        ]
    }
    ```

#### List Pending Friend Requests

- `GET /social/api/v1/pending-friend-requests/`
  - Description: List all pending friend requests received by the current user.
  - Response:
    ```json
    {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 2,
                "from_user": {
                    "id": 4,
                    "email": "sender@example.com",
                    "name": "Sender Name"
                },
                "to_user": {
                    "id": 2,
                    "email": "anotheruser@example.com",
                    "name": "Receiver Name"
                }
            }
        ]
    }
    ```

### Rate Limiting

- Users cannot send more than 3 friend requests within a minute.

## Technologies Used

- Python
- Django
- Django Rest Framework
- PostgreSQL
- Docker
- Docker Compose
- Git Version Control
 
