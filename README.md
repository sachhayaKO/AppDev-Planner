# AppDev Planner — Habit Tracking API

A Dockerized Flask backend for managing users, habits, and daily habit completions.  
This project exposes a clean REST API and is deployable locally or on a cloud VM using Docker & Docker Compose.

---

## 🚀 Running the Application

### Run with Docker (recommended)

Pull the published image:
```bash
docker pull sachhayako/appdev-planner:v1.0.1
```

Run with Docker Compose:
```bash
docker compose up -d
```

The server will be available at:
```
http://<YOUR_VM_IP>/
```

---

## 📘 API Specification

All responses are JSON.  
Base URL:
```
http://<YOUR_VM_IP>/
```

---

## 1. Create a New User
### POST `/users`

#### Request Body
```json
{
  "name": "Sachin",
  "email": "sachin@example.com"
}
```

#### Response
```json
{
  "id": 1,
  "name": "Sachin",
  "email": "sachin@example.com"
}
```

---

## 2. Get User by ID
### GET `/users/<user_id>`

#### Response
```json
{
  "id": 1,
  "name": "Sachin",
  "email": "sachin@example.com"
}
```

---

## 3. Create a Global Habit
### POST `/habits`

#### Request Body
```json
{
  "name": "Workout",
  "description": "Go to the gym for 30 minutes"
}
```

#### Response
```json
{
  "id": 2,
  "name": "Workout",
  "description": "Go to the gym for 30 minutes"
}
```

---

## 4. Get All Global Habits
### GET `/habits`

#### Response
```json
[
  {
    "id": 1,
    "name": "Drink Water",
    "description": "Drink 8 cups of water"
  },
  {
    "id": 2,
    "name": "Workout",
    "description": "Go to the gym"
  }
]
```

---

## 5. Assign a Habit to a User
### POST `/users/<user_id>/habits`

#### Request Body
```json
{
  "habit_id": 1
}
```

#### Response
```json
{
  "message": "Habit assigned successfully."
}
```

---

## 6. Get All Habits Assigned to a User
### GET `/users/<user_id>/habits`

#### Response
```json
[
  {
    "habit_id": 1,
    "name": "Drink Water",
    "description": "Drink 8 cups of water",
    "completed_today": false
  }
]
```

---

## 7. Mark Habit as Completed for Today
### POST `/users/<user_id>/habits/<habit_id>/complete`

#### Response
```json
{
  "message": "Habit marked as completed for today."
}
```

---

## 8. Get Daily Completion History for a User
### GET `/users/<user_id>/completions`

#### Response
```json
[
  {
    "habit_id": 1,
    "habit_name": "Drink Water",
    "date": "2025-12-05"
  }
]
```

---

## 📁 Project Structure

```
src/
│── app.py
│── db.py
│── models.py
│── routes/
│── __init__.py
Dockerfile
docker-compose.yml
requirements.txt
```

---

## 🐳 Docker Image

```
sachhayako/appdev-planner:v1.0.1
```

---

## 📝 Notes for Graders

- All API routes are documented above.  
- Application runs on **port 80 (external)** → **port 5000 (internal)**.  
- Fully testable via Postman or curl.  
- SQLite database stored inside the container.
