# 🐳 Docker Testing Guide - Multi-Tenant SaaS Platform

## ✅ System Status

Your application is now running in Docker with all services!

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Nginx Reverse Proxy**: http://localhost:80
- **pgAdmin Web UI**: http://localhost:5050
- **PostgreSQL Database**: localhost:5432
- **Container Status**: ✅ All Running

---

## 🚀 Quick Start

### Start All Services

```bash
cd /Users/admin/Desktop/multitenant
docker-compose up -d
```

This will start:
- ✅ PostgreSQL database (multitenant_postgres)
- ✅ pgAdmin web interface (multitenant_pgadmin)
- ✅ Flask backend API (multitenant_backend)
- ✅ React frontend (multitenant_frontend)
- ✅ Nginx reverse proxy (multitenant_nginx)

### Check Service Status

```bash
docker-compose ps
```

All services should show "Up" status.

---

## 📊 STEP 1: Access pgAdmin Web Interface

### 1.1 Open pgAdmin in Browser

Navigate to: **http://localhost:5050**

**Login Credentials:**
- **Email:** `admin@multitenant.com`
- **Password:** `Admin@12345`

### 1.2 Add Database Server Connection

1. After logging in, right-click on **"Servers"** in the left panel
2. Select **"Create" → "Server..."**

### 1.3 Configure Connection

**In the "General" tab:**

- **Name:** `Multitenant Database`

**In the "Connection" tab:**

- **Host name/address:** `postgres` (Docker service name)
- **Port:** `5432`
- **Maintenance database:** `multitenant_db`
- **Username:** `postgres`
- **Password:** `Saketh12@`
- ✅ Check "Save password"

### 1.4 Click "Save"

You should now see "Multitenant Database" in your servers list!

### 1.5 Explore the Database

Navigate to:

```
Servers → Multitenant Database → Databases → multitenant_db → Schemas → public → Tables
```

You should see 3 tables:

- ✅ `admins` - Contains default admin account
- ✅ `tenants` - Empty (will add data via API)
- ✅ `customers` - Empty (will add data via API)

---

## 🧪 STEP 2: Test APIs with Postman

### 2.1 Test Health Check

```
Method: GET
URL: http://localhost:5001/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "message": "Multi-tenant SaaS API is running"
}
```

### 2.2 Admin Login

```
Method: POST
URL: http://localhost:5001/api/admin/login
Headers: Content-Type: application/json
Body (raw JSON):
{
  "email": "admin@multitenant.com",
  "password": "Admin@12345"
}
```

**Expected Response:**

```json
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "admin": {
    "id": 1,
    "email": "admin@multitenant.com",
    "name": "System Administrator",
    "is_active": true
  }
}
```

**📋 COPY THE TOKEN!** You'll need it for the next requests.

### 2.3 Create Your First Tenant

```
Method: POST
URL: http://localhost:5001/api/admin/tenants
Headers:
  - Content-Type: application/json
  - Authorization: Bearer YOUR_TOKEN_HERE
Body (raw JSON):
{
  "name": "Nivea Hair Care",
  "email": "info@nivea.com",
  "phone": "9876543210",
  "admin_name": "John Doe",
  "admin_email": "john@nivea.com",
  "admin_password": "Nivea@12345",
  "metadata": {
    "gst": "29ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "address": "Mumbai, India"
  }
}
```

**Expected Response:**

```json
{
  "message": "Tenant created successfully",
  "tenant": {
    "id": 1,
    "name": "Nivea Hair Care",
    "slug": "nivea-hair-care",
    "email": "info@nivea.com",
    ...
  }
}
```

### 2.4 Get All Tenants

```
Method: GET
URL: http://localhost:5001/api/admin/tenants
Headers:
  - Authorization: Bearer YOUR_TOKEN_HERE
```

### 2.5 Tenant Login

```
Method: POST
URL: http://localhost:5001/api/tenant/login
Headers: Content-Type: application/json
Body (raw JSON):
{
  "email": "john@nivea.com",
  "password": "Nivea@12345"
}
```

**📋 COPY THE NEW TOKEN!** This is the tenant token.

### 2.6 Create Customer (as Tenant)

```
Method: POST
URL: http://localhost:5001/api/tenant/customers
Headers:
  - Content-Type: application/json
  - Authorization: Bearer TENANT_TOKEN_HERE
Body (raw JSON):
{
  "name": "Bob Smith",
  "email": "bob@customer.com",
  "phone": "9123456789",
  "password": "Customer@123",
  "role": "customer",
  "access_level": "basic"
}
```

### 2.7 Customer Login

```
Method: POST
URL: http://localhost:5001/api/customer/login
Headers: Content-Type: application/json
Body (raw JSON):
{
  "email": "bob@customer.com",
  "password": "Customer@123",
  "tenant_id": 1
}
```

---

## 🔍 STEP 3: Verify Data in pgAdmin4

### 3.1 Check Admins Table

1. In pgAdmin4, navigate to: `Tables → admins`
2. Right-click → **"View/Edit Data"** → **"All Rows"**
3. You should see 1 admin record

### 3.2 Check Tenants Table

1. Navigate to: `Tables → tenants`
2. Right-click → **"View/Edit Data"** → **"All Rows"**
3. You should see "Nivea Hair Care" and other tenants you created

### 3.3 Check Customers Table

1. Navigate to: `Tables → customers`
2. Right-click → **"View/Edit Data"** → **"All Rows"**
3. You should see "Bob Smith" and other customers

---

## 📊 STEP 4: Check Docker Container Status

### 4.1 View Running Containers

```bash
docker ps
```

You should see 5 containers running:

- `multitenant_postgres` - PostgreSQL Database
- `multitenant_pgadmin` - pgAdmin Web UI
- `multitenant_backend` - Flask API
- `multitenant_frontend` - React App
- `multitenant_nginx` - Reverse Proxy

### 4.2 View Logs

```bash
# All services
docker-compose logs -f

# Specific service logs
docker logs multitenant_backend
docker logs multitenant_frontend
docker logs multitenant_postgres
docker logs multitenant_pgadmin
docker logs multitenant_nginx
```

### 4.3 Stop All Containers

```bash
cd /Users/admin/Desktop/multitenant
docker-compose down
```

### 4.4 Start All Containers

```bash
cd /Users/admin/Desktop/multitenant
docker-compose up -d
```

### 4.5 Rebuild and Restart (if you made code changes)

```bash
docker-compose down
docker-compose up -d --build
```

### 4.6 View Resource Usage

```bash
docker stats
```

---

## 🎯 Complete API Endpoints

### Admin APIs

| Method | Endpoint                 | Auth  | Description      |
| ------ | ------------------------ | ----- | ---------------- |
| POST   | `/api/admin/login`       | No    | Admin login      |
| GET    | `/api/admin/tenants`     | Admin | Get all tenants  |
| GET    | `/api/admin/tenants/:id` | Admin | Get tenant by ID |
| POST   | `/api/admin/tenants`     | Admin | Create tenant    |
| PUT    | `/api/admin/tenants/:id` | Admin | Update tenant    |
| DELETE | `/api/admin/tenants/:id` | Admin | Delete tenant    |
| GET    | `/api/admin/dashboard`   | Admin | Dashboard stats  |

### Tenant APIs

| Method | Endpoint                    | Auth   | Description       |
| ------ | --------------------------- | ------ | ----------------- |
| POST   | `/api/tenant/login`         | No     | Tenant login      |
| GET    | `/api/tenant/profile`       | Tenant | Get profile       |
| PUT    | `/api/tenant/profile`       | Tenant | Update profile    |
| GET    | `/api/tenant/customers`     | Tenant | Get all customers |
| POST   | `/api/tenant/customers`     | Tenant | Create customer   |
| PUT    | `/api/tenant/customers/:id` | Tenant | Update customer   |
| DELETE | `/api/tenant/customers/:id` | Tenant | Delete customer   |
| GET    | `/api/tenant/dashboard`     | Tenant | Dashboard stats   |

### Customer APIs

| Method | Endpoint                        | Auth     | Description       |
| ------ | ------------------------------- | -------- | ----------------- |
| POST   | `/api/customer/login`           | No       | Customer login    |
| POST   | `/api/customer/register`        | No       | Self-registration |
| GET    | `/api/customer/profile`         | Customer | Get profile       |
| PUT    | `/api/customer/profile`         | Customer | Update profile    |
| POST   | `/api/customer/change-password` | Customer | Change password   |

---

## 🔧 Troubleshooting

### Problem: Container won't start

**Solution:**

```bash
docker-compose down
docker-compose up -d --build
```

### Problem: Port already in use

**Solution:**

```bash
# Find process using port
lsof -i :5001  # Backend
lsof -i :3000  # Frontend
lsof -i :5050  # pgAdmin
lsof -i :5432  # PostgreSQL
lsof -i :80    # Nginx

# Kill process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Problem: Database connection failed

**Solution:**

```bash
# Restart containers
docker-compose restart

# Or reset database (WARNING: Deletes all data!)
docker-compose down -v
docker-compose up -d
```

### Problem: Can't access pgAdmin at localhost:5050

**Solution:**

- Verify pgAdmin container is running: `docker ps | grep pgadmin`
- Check pgAdmin logs: `docker logs multitenant_pgadmin`
- Wait 30 seconds for pgAdmin to fully initialize
- Try accessing: http://127.0.0.1:5050

### Problem: Can't connect database in pgAdmin

**Solution:**

- Use **`postgres`** as hostname (NOT `localhost`)
- This is the Docker service name for internal networking
- Verify network: `docker network inspect multitenant_multitenant_network`

### Problem: Frontend not loading

**Solution:**

```bash
# Check if node_modules are installed
docker exec multitenant_frontend ls /app/node_modules

# Rebuild frontend
docker-compose up -d --build frontend

# Check logs
docker logs multitenant_frontend -f
```

### Problem: Nginx 502 Bad Gateway

**Solution:**

```bash
# Ensure backend and frontend are running
docker-compose ps

# Restart nginx
docker-compose restart nginx

# Check nginx logs
docker logs multitenant_nginx
```

### Problem: Backend crashes on startup

**Solution:**

```bash
# Check backend logs
docker logs multitenant_backend

# Common issue: Database not ready
# Solution: Wait for postgres healthcheck
# The docker-compose.yml already handles this with depends_on condition

# Restart backend
docker-compose restart backend
```

---

## 🎉 Success Checklist

- ✅ All 5 Docker containers running
- ✅ Frontend accessible at http://localhost:3000
- ✅ Backend API responding at http://localhost:5001
- ✅ Nginx proxy working at http://localhost:80
- ✅ pgAdmin web UI at http://localhost:5050
- ✅ PostgreSQL accessible at localhost:5432
- ✅ pgAdmin connected to database
- ✅ Admin login successful
- ✅ Tenant created and login successful
- ✅ Customer created and login successful
- ✅ Data visible in pgAdmin tables

---

## 🌐 All Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | N/A |
| **Backend API** | http://localhost:5001 | N/A |
| **Nginx** | http://localhost:80 | N/A |
| **pgAdmin** | http://localhost:5050 | admin@multitenant.com / Admin@12345 |
| **PostgreSQL** | localhost:5432 | postgres / Saketh12@ |

---

## 📦 Docker Commands Reference

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker logs multitenant_backend -f

# Restart a service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build

# Remove all containers and volumes (⚠️ DELETES DATA)
docker-compose down -v

# View running containers
docker ps

# View resource usage
docker stats

# Execute command in container
docker exec -it multitenant_backend bash

# Access PostgreSQL CLI
docker exec -it multitenant_postgres psql -U postgres -d multitenant_db
```

---

**🎊 Congratulations! Your Multi-Tenant SaaS Platform is fully operational in Docker!**

Now you can:

1. ✅ Access the React frontend at http://localhost:3000
2. ✅ Test all APIs at http://localhost:5001
3. ✅ Manage database via pgAdmin at http://localhost:5050
4. ✅ Use Nginx reverse proxy at http://localhost:80
5. ✅ Deploy to production

**Next Steps:**

- Integrate frontend with backend APIs
- Add email notifications
- Implement advanced features (AI/ML)
- Set up CI/CD pipeline
- Deploy to cloud (AWS/Azure/GCP)
- Enable HTTPS with SSL certificates
