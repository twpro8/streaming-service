
## 🚀 Quickstart

This project is a microservices-based **streaming platform**, including:

* **Auth Service** — authentication and user management
* **Catalog Service** — movies and series catalog
* **Redis** — cache and Celery broker
* **PostgreSQL** — main database
* **Celery Worker / Beat** — background task processing

---

### Requirements

* Docker 24+
* Docker Compose 2+
* Git

---

### 📥 Clone the repository

```bash
git clone https://github.com/twpro8/streaming-service.git
cd streaming-service
```

---

### 🔐 Environment variables

Create root `.env` (used by Redis/PostgreSQL):

```bash
cp .env-example .env
```

---

### ▶️ Run all services

```bash
docker compose up --build -d
```

Docker automatically waits for **PostgreSQL** and **Redis** to become healthy ✅

---

### 🌍 URLs

| Service         | Base URL                                       | Swagger Docs                                             |
| --------------- | ---------------------------------------------- | -------------------------------------------------------- |
| Auth Service    | [http://127.0.0.1:8000](http://127.0.0.1:8000) | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| Catalog Service | [http://127.0.0.1:8001](http://127.0.0.1:8001) | [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) |

---

### 🔍 View logs

```bash
docker compose logs -f
```

---

### Stop

```bash
docker compose down
```

To remove local data as well:

```bash
docker compose down -v
```

---

### Check running containers

```bash
docker ps
```

---

🎉 Congratulations! Streaming Service is now up and running on your machine! 🎉

---
