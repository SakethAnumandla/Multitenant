# 🚀 Multi-Tenant SaaS Platform - Complete Setup Guide

Welcome! This guide will walk you through setting up and running the entire multi-tenant SaaS platform step by step.

---

## ✅ Prerequisites Check

Before starting, ensure you have:

- ✅ PostgreSQL installed (with password: `Saketh12@`)
- ✅ Docker Desktop installed and running
- ✅ Postman Desktop installed (for API testing)
- ✅ VS Code or Cursor IDE installed

---

## 📋 STEP-BY-STEP SETUP

### **STEP 1: Create Database in pgAdmin**

1. Open **pgAdmin 4**
2. Connect to your PostgreSQL server (localhost:5432)
3. Right-click on "Databases" → "Create" → "Database"
4. Database name: `multitenant_db`
5. Click "Save"

**✋ Once done, type "done" to continue to Step 2**

---

### **STEP 2: Setup Backend (Without Docker)**

#### A. Create Virtual Environment

```bash
cd /Users/admin/Desktop/multitenant/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
```

#### B. Install Dependencies

```bash
pip install -r requirements.txt
```

#### C. Run the Backend Server

```bash
python app/main.py
```

**Expected Output:**

```
==================================================
🚀 Starting Multi-tenant SaaS Platform API
==================================================
📍 Running on: http://0.0.0.0:5000
🔧 Debug Mode: True
📊 Database: multitenant_db
==================================================
✅ Database tables created successfully!
✅ Default admin created: admin@multitenant.com
```

**Backend is now running on: http://localhost:5000**

**✋ Keep this terminal open. Open a new terminal for the next steps.**

---

### **STEP 3: Test Backend with Postman**

#### Test 1: Health Check

```
Method: GET
URL: http://localhost:5000/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "message": "Multi-tenant SaaS API is running"
}
```

#### Test 2: Admin Login

```
Method: POST
URL: http://localhost:5000/api/admin/login
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

**Copy the `token` value - you'll need it for the next requests!**

#### Test 3: Create Tenant (Requires Admin Token)

```
Method: POST
URL: http://localhost:5000/api/admin/tenants
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
    ...
  }
}
```

#### Test 4: Tenant Login

```
Method: POST
URL: http://localhost:5000/api/tenant/login
Headers: Content-Type: application/json
Body (raw JSON):
{
  "email": "john@nivea.com",
  "password": "Nivea@12345"
}
```

**✋ Once backend testing is complete, type "done" to continue to Frontend setup**

---

### **STEP 4: Setup Frontend**

Open a **NEW terminal** (keep backend running):

```bash
cd /Users/admin/Desktop/multitenant/frontend

# Install dependencies
npm install

# Start React development server
npm start
```

**Expected Output:**

```
Compiled successfully!

You can now view multitenant-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Frontend is now running on: http://localhost:3000**

Your browser should automatically open to `http://localhost:3000`

**✋ Once frontend opens in browser, type "done" to continue**

---

### **STEP 5: Test Frontend Application**

#### Test 1: Admin Portal

1. Go to http://localhost:3000
2. Click "Admin Login"
3. Enter credentials:
   - Email: `admin@multitenant.com`
   - Password: `Admin@12345`
4. Click "Login"
5. You should see the **Admin Dashboard** with statistics and tenant list

#### Test 2: Create Tenant via UI

1. In Admin Dashboard, click "+ Create Tenant"
2. Fill in the form:
   - Business Name: `TCS Hair Solutions`
   - Business Email: `info@tcs.com`
   - Phone: `9876543210`
   - Admin Name: `Alice Johnson`
   - Admin Email: `alice@tcs.com`
   - Admin Password: `TCS@12345`
   - GST: `29ABCDE1234F1Z5` (optional)
   - PAN: `ABCDE1234F` (optional)
3. Click "Create Tenant"
4. You should see success message and new tenant in the list

#### Test 3: Tenant Login

1. Logout from Admin (click Logout in navbar)
2. Go to Home → Click "Tenant Login"
3. Enter credentials:
   - Email: `alice@tcs.com`
   - Password: `TCS@12345`
4. Click "Login"
5. You should see the **Tenant Dashboard**

#### Test 4: Create Customer/Employee

1. In Tenant Dashboard, click "+ Add User"
2. Fill in the form:
   - Name: `Bob Smith`
   - Email: `bob@customer.com`
   - Phone: `9123456789`
   - Role: `Customer`
   - Password: `Customer@123`
   - Access Level: `Basic`
3. Click "Create User"
4. You should see the new user in the list

#### Test 5: Customer Login

1. Logout from Tenant
2. Go to Home → Click "Customer Login"
3. Enter credentials:
   - Email: `bob@customer.com`
   - Password: `Customer@123`
4. Click "Login"
5. You should see the **Customer Dashboard** with profile

**✋ Once all frontend tests pass, type "done" to continue**

---

### **STEP 6: Setup with Docker (Optional)**

If you want to run everything with Docker:

```bash
cd /Users/admin/Desktop/multitenant

# Stop any running backend/frontend servers first (Ctrl+C)

# Start all services with Docker
docker-compose up -d

# Check if containers are running
docker ps

# View logs
docker-compose logs -f
```

**Services will be available at:**

- Backend API: http://localhost:5000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

**To stop Docker containers:**

```bash
docker-compose down
```

---

## 📊 Complete API Reference

### Admin APIs

| Method | Endpoint                 | Description      | Auth Required |
| ------ | ------------------------ | ---------------- | ------------- |
| POST   | `/api/admin/login`       | Admin login      | No            |
| GET    | `/api/admin/tenants`     | Get all tenants  | Yes (Admin)   |
| GET    | `/api/admin/tenants/:id` | Get tenant by ID | Yes (Admin)   |
| POST   | `/api/admin/tenants`     | Create tenant    | Yes (Admin)   |
| PUT    | `/api/admin/tenants/:id` | Update tenant    | Yes (Admin)   |
| DELETE | `/api/admin/tenants/:id` | Delete tenant    | Yes (Admin)   |
| GET    | `/api/admin/dashboard`   | Dashboard stats  | Yes (Admin)   |

### Tenant APIs

| Method | Endpoint                    | Description        | Auth Required |
| ------ | --------------------------- | ------------------ | ------------- |
| POST   | `/api/tenant/login`         | Tenant login       | No            |
| GET    | `/api/tenant/profile`       | Get profile        | Yes (Tenant)  |
| PUT    | `/api/tenant/profile`       | Update profile     | Yes (Tenant)  |
| GET    | `/api/tenant/customers`     | Get all customers  | Yes (Tenant)  |
| GET    | `/api/tenant/customers/:id` | Get customer by ID | Yes (Tenant)  |
| POST   | `/api/tenant/customers`     | Create customer    | Yes (Tenant)  |
| PUT    | `/api/tenant/customers/:id` | Update customer    | Yes (Tenant)  |
| DELETE | `/api/tenant/customers/:id` | Delete customer    | Yes (Tenant)  |
| GET    | `/api/tenant/dashboard`     | Dashboard stats    | Yes (Tenant)  |

### Customer APIs

| Method | Endpoint                        | Description           | Auth Required  |
| ------ | ------------------------------- | --------------------- | -------------- |
| POST   | `/api/customer/login`           | Customer login        | No             |
| POST   | `/api/customer/login/:slug`     | Login via tenant slug | No             |
| POST   | `/api/customer/register`        | Self-registration     | No             |
| POST   | `/api/customer/reset-password`  | Reset password        | No             |
| GET    | `/api/customer/profile`         | Get profile           | Yes (Customer) |
| PUT    | `/api/customer/profile`         | Update profile        | Yes (Customer) |
| POST   | `/api/customer/change-password` | Change password       | Yes (Customer) |

---

## 🔧 Troubleshooting

### Backend Issues

**Problem:** `Database connection failed`
**Solution:**

- Check if PostgreSQL is running
- Verify database name: `multitenant_db`
- Check password in `.env` file: `Saketh12@`
- Run: `createdb multitenant_db` if database doesn't exist

**Problem:** `ModuleNotFoundError`
**Solution:**

- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Frontend Issues

**Problem:** `npm: command not found`
**Solution:** Install Node.js from https://nodejs.org/

**Problem:** `Cannot connect to backend`
**Solution:**

- Ensure backend is running on http://localhost:5000
- Check `.env` file in frontend folder
- Clear browser cache

### Docker Issues

**Problem:** `Cannot connect to Docker daemon`
**Solution:** Start Docker Desktop application

**Problem:** `Port already in use`
**Solution:** Stop running services or change ports in `docker-compose.yml`

---

## 🎯 Default Credentials

### Admin

- **Email:** admin@multitenant.com
- **Password:** Admin@12345

### Tenant (After creation)

- **Email:** [admin_email from creation]
- **Password:** [admin_password from creation]

### Customer (After creation)

- **Email:** [email from registration]
- **Password:** [password from registration]

---

## 📝 Next Steps

1. ✅ Test all APIs in Postman
2. ✅ Test all frontend pages
3. ✅ Create multiple tenants
4. ✅ Create customers for each tenant
5. ✅ Test role-based access control
6. 🔄 Setup Git repository
7. 🔄 Deploy to production
8. 🔄 Add email notifications
9. 🔄 Integrate AI/ML for hair analysis

---

## 📞 Support

If you encounter any issues:

1. Check this guide thoroughly
2. Review error messages in terminal
3. Check browser console for frontend errors
4. Verify all services are running

---

**🎉 Congratulations! Your multi-tenant SaaS platform is now fully set up and running!**

Now you can test it step by step and let me know when you're ready for the next phase.
