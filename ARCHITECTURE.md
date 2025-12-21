# PROJECT AND DATABASE ARCHITECTURE

# PROJECT ARCHITECTURE

The application is built using a three-tier architecture pattern:

1. FRONTEND LAYER (React)

   - Technology: React JavaScript framework
   - Location: frontend/ folder
   - Purpose: User interface that users interact with
   - Components: Login pages, dashboards, test-taking interface
   - Communication: Sends HTTP requests to backend API

2. BACKEND LAYER (Python Flask)

   - Technology: Flask web framework
   - Location: backend/app/ folder
   - Purpose: Business logic, API endpoints, data processing
   - Structure:
     - routes/ - API endpoints organized by feature
     - models/ - Database table definitions
     - utils/ - Helper functions (authentication, validation, RBAC)
     - config.py - Application configuration
   - Communication: Receives requests from frontend, talks to database

3. DATABASE LAYER (PostgreSQL)

   - Technology: PostgreSQL relational database
   - Purpose: Stores all application data permanently
   - Communication: Backend reads and writes data

4. REVERSE PROXY (Nginx)
   - Purpose: Routes incoming requests to correct service
   - Handles: Frontend static files and backend API requests

## HOW THEY WORK TOGETHER:

User Browser
|
| HTTP Requests
|
Nginx (Port 80)
|
| Routes to
|
Frontend (React) - Port 3000 Backend (Flask) - Port 5001
| |
| API Calls | SQL Queries
| |
+----------------------------------------+
|
|
PostgreSQL (Port 5432)

# DATABASE ARCHITECTURE

The database uses a relational model with 6 main tables:

1. ADMINS TABLE
   Purpose: Stores system administrators who manage the entire platform
   Key Fields:

   - id: Unique identifier
   - email: Admin email address (unique)
   - password: Hashed password
   - name: Admin name
   - is_active: Whether admin account is active
     Relationships: None (top-level entity)

2. TENANTS TABLE
   Purpose: Stores organizations or businesses using the platform
   Key Fields:

   - id: Unique identifier
   - name: Company name
   - slug: URL-friendly identifier (like company-name)
   - email: Company email
   - phone: Company phone
   - business_metadata: JSON field storing GST, PAN, address, etc.
   - admin_name: Tenant admin person name
   - admin_email: Tenant admin email (unique)
   - admin_password: Tenant admin password (hashed)
   - is_active: Whether tenant account is active
   - subscription_status: trial, active, suspended, cancelled
     Relationships:
   - Has many Users (one tenant can have many users)
   - Has many Tests (one tenant can have many tests)
   - Has many AccessMatrix entries

3. USERS TABLE
   Purpose: Stores all end users (employees, managers, regular users)
   Key Fields:

   - id: Unique identifier
   - tenant_id: Which tenant this user belongs to (foreign key)
   - name: User name
   - email: User email (unique within tenant)
   - phone: User phone
   - password: Hashed password
   - profile_data: JSON field for additional user info
   - role: user, employee, manager, sales_rep
   - access_level: basic, premium, admin
   - is_active: Whether user account is active
   - temp_password: Temporary password for employee onboarding
   - password_reset_required: Flag for first-time login
     Relationships:
   - Belongs to one Tenant (many-to-one)
   - Has many TestResponses (one user can take many tests)

4. TESTS TABLE
   Purpose: Stores test/questionnaire definitions
   Key Fields:

   - id: Unique identifier
   - tenant_id: Which tenant owns this test (foreign key)
   - title: Test title
   - description: Test description
   - is_active: Whether test is currently active
     Relationships:
   - Belongs to one Tenant (many-to-one)
   - Has many Questions (one test has many questions)
   - Has many TestResponses (one test can have many responses)

5. QUESTIONS TABLE
   Purpose: Stores individual questions within tests
   Key Fields:

   - id: Unique identifier
   - test_id: Which test this question belongs to (foreign key)
   - question_text: The actual question
   - question_type: text, radio, checkbox, range, textarea
   - section: Which section the question is in
   - options: JSON array of answer options (for radio/checkbox)
   - priority_order: Order in which question appears
   - is_required: Whether question must be answered
   - placeholder: Placeholder text for input fields
     Relationships:
   - Belongs to one Test (many-to-one)

6. TEST_RESPONSES TABLE
   Purpose: Stores user answers to tests
   Key Fields:

   - id: Unique identifier
   - test_id: Which test was taken (foreign key)
   - user_id: Which user took the test (foreign key)
   - responses: JSON object storing answers {question_id: answer}
   - image_path: Path to uploaded image file
   - image_url: URL to access uploaded image
   - is_completed: Whether test is finished
   - started_at: When test was started
   - completed_at: When test was completed
     Relationships:
   - Belongs to one Test (many-to-one)
   - Belongs to one User (many-to-one)

7. ACCESS_MATRIX TABLE
   Purpose: Defines what each role can do (Role-Based Access Control)
   Key Fields:
   - id: Unique identifier
   - tenant_id: Which tenant this applies to (null for global permissions)
   - role: super_admin, tenant_admin, manager, employee, user
   - permissions: JSON object defining what actions are allowed
   - description: Description of the role permissions
   - is_active: Whether this permission set is active
     Relationships:
   - Belongs to one Tenant (optional, many-to-one, null for global)

## DATABASE RELATIONSHIPS DIAGRAM:

Admins (standalone)
|
|
Tenants
|
|---> Users (one tenant has many users)
| |
| |---> TestResponses (one user has many responses)
|
|---> Tests (one tenant has many tests)
| |
| |---> Questions (one test has many questions)
| |
| |---> TestResponses (one test has many responses)
|
|---> AccessMatrix (one tenant has many permission sets)

# KEY ARCHITECTURAL CONCEPTS:

1. MULTI-TENANCY

   - Each tenant (organization) has isolated data
   - All tenant-related data includes tenant_id
   - Users can only access data from their tenant
   - Tests and responses are scoped to tenants

2. ROLE-BASED ACCESS CONTROL (RBAC)

   - AccessMatrix table defines permissions per role
   - Roles: super_admin, tenant_admin, manager, employee, user
   - Permissions specify what each role can do (create, read, update, delete)
   - Can be global or tenant-specific

3. CASCADE DELETION

   - If a tenant is deleted, all related users, tests, and responses are deleted
   - If a test is deleted, all related questions and responses are deleted
   - This ensures data consistency

4. JSON FIELDS

   - business_metadata: Flexible storage for tenant business info
   - profile_data: Flexible storage for user profile information
   - options: Flexible storage for question answer options
   - responses: Flexible storage for test answers
   - permissions: Flexible storage for role permissions

5. SOFT DELETE
   - Users and tenants use is_active flag instead of hard deletion
   - Allows data recovery and auditing

# DATA FLOW EXAMPLE (User Taking a Test):

1. User logs in through frontend
2. Frontend calls POST /api/user/login
3. Backend validates credentials, returns JWT token
4. User selects a test
5. Frontend calls POST /api/test/tests/{test_id}/start
6. Backend creates TestResponse record in database
7. Backend returns test questions
8. User answers questions
9. Frontend calls POST /api/test/responses/{response_id}/answers
10. Backend updates TestResponse.responses JSON field
11. User submits test
12. Frontend calls POST /api/test/responses/{response_id}/complete
13. Backend marks TestResponse.is_completed = True
14. Database stores all answers permanently

# STORAGE LOCATIONS:

Database (PostgreSQL):

- All structured data (users, tenants, tests, questions, responses)
- Runs in Docker container
- Data persisted in Docker volume

File System:

- Uploaded images stored in backend/uploads/test_images/
- Image paths stored in database
- Images served through API endpoint

# SUMMARY:

This is a multi-tenant SaaS application where:

- Multiple organizations (tenants) can use the same platform
- Each tenant's data is isolated
- Different user roles have different permissions
- Users can create and take tests/questionnaires
- Everything is secured with JWT authentication
- All data is stored in PostgreSQL database
- Frontend and backend communicate via REST API
