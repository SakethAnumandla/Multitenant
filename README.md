# Multi-Tenant SaaS Platform

A secure and scalable multi-tenant B2B SaaS platform for hair/scalp analysis with authentication, data isolation, and role-based access control.

## 🏗️ Architecture

### Three-Tier System

1. **Admin Module**: System administrators manage tenants and monitor platform activity
2. **Tenant Module**: Businesses (brands) manage their employees and customers
3. **Customer Module**: End-users interact with tenant-specific services

## 🚀 Features

### Admin Module

- Hardcoded admin account with secure authentication
- Create, edit, and delete tenants
- Monitor system-wide activity
- View dashboard statistics

### Tenant Module

- Tenant registration with business details (GST, PAN, etc.)
- SEO-friendly URLs using slugs
- Employee and customer management
- Role-based access control
- Dashboard and reporting

### Customer Module

- Email/phone authentication with JWT tokens
- Profile management
- Self-registration for customers
- Employee onboarding with temporary passwords
- Role-based data access

## 🛠️ Tech Stack

### Backend

- **Framework**: Flask (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Security**: bcrypt password hashing
- **Validation**: email-validator, regex patterns

### Frontend

- **Framework**: React.js
- **Styling**: CSS (Modern UI/UX)

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Database**: PostgreSQL 15

## 📁 Project Structure

```
multitenant/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── utils/          # Auth & validators
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # DB connection
│   │   └── main.py         # App entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/               # React application
├── nginx/                  # Nginx configuration
└── docker-compose.yml
```

## 🔧 Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd multitenant
```

### 2. Backend Setup

#### Option A: Local Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup .env file (already created)
# Update DATABASE_PASSWORD and JWT_SECRET_KEY

# Create database
createdb multitenant_db

# Run application
python app/main.py
```

#### Option B: Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### 3. Database Setup

The database tables will be created automatically when you run the application for the first time.

**Default Admin Credentials:**

- Email: `admin@multitenant.com`
- Password: `Admin@12345`

### 4. Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm start
```

## 📡 API Endpoints

### Admin Endpoints

| Method | Endpoint                 | Description       |
| ------ | ------------------------ | ----------------- |
| POST   | `/api/admin/login`       | Admin login       |
| GET    | `/api/admin/tenants`     | Get all tenants   |
| GET    | `/api/admin/tenants/:id` | Get tenant by ID  |
| POST   | `/api/admin/tenants`     | Create new tenant |
| PUT    | `/api/admin/tenants/:id` | Update tenant     |
| DELETE | `/api/admin/tenants/:id` | Delete tenant     |
| GET    | `/api/admin/dashboard`   | Dashboard stats   |

### Tenant Endpoints

| Method | Endpoint                    | Description              |
| ------ | --------------------------- | ------------------------ |
| POST   | `/api/tenant/login`         | Tenant login             |
| GET    | `/api/tenant/profile`       | Get tenant profile       |
| PUT    | `/api/tenant/profile`       | Update profile           |
| GET    | `/api/tenant/customers`     | Get all customers        |
| GET    | `/api/tenant/customers/:id` | Get customer by ID       |
| POST   | `/api/tenant/customers`     | Create customer/employee |
| PUT    | `/api/tenant/customers/:id` | Update customer          |
| DELETE | `/api/tenant/customers/:id` | Delete customer          |
| GET    | `/api/tenant/dashboard`     | Dashboard stats          |

### Customer Endpoints

| Method | Endpoint                        | Description                 |
| ------ | ------------------------------- | --------------------------- |
| POST   | `/api/customer/login`           | Customer login              |
| POST   | `/api/customer/login/:slug`     | Login via tenant slug       |
| POST   | `/api/customer/register`        | Self-registration           |
| POST   | `/api/customer/reset-password`  | Reset password (first-time) |
| GET    | `/api/customer/profile`         | Get profile                 |
| PUT    | `/api/customer/profile`         | Update profile              |
| POST   | `/api/customer/change-password` | Change password             |

## 🔐 Authentication

All protected endpoints require JWT token in Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## 🧪 Testing with Postman

1. Import the API collection (coming soon)
2. Set environment variable `base_url` to `http://localhost:5000`
3. Start testing!

### Example: Admin Login

```bash
POST http://localhost:5000/api/admin/login
Content-Type: application/json

{
  "email": "admin@multitenant.com",
  "password": "Admin@12345"
}
```

## 🌐 Database Schema

### Admins Table

- id, email, password, name, is_active, created_at, updated_at

### Tenants Table

- id, name, slug, email, phone, metadata (JSON), admin_name, admin_email, admin_password, is_active, subscription_status, created_at, updated_at

### Customers Table

- id, tenant_id, name, email, phone, password, profile_data (JSON), role, access_level, is_active, is_verified, temp_password, password_reset_required, last_login, created_at, updated_at

## 🔄 Future Enhancements

- OAuth 2.0 integration
- Apache Cassandra for analytics
- Redis for caching
- Email service for notifications
- AI/ML integration for hair analysis
- Mobile app (Flutter)

## 👥 Team

- Development Team: Building the future of scalable SaaS platforms

## 📝 License

This project is proprietary and confidential.

## 🆘 Support

For issues and questions, contact the development team.

---

**Built with ❤️ by the Multi-tenant SaaS Team**
