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
