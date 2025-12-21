DATABASE ARCHITECTURE DOCUMENTATION
====================================

DATABASE OVERVIEW
=================

Database Type: PostgreSQL 15
Database Name: multitenant_db
Architecture: Relational Database Management System (RDBMS)
ORM Framework: SQLAlchemy (Flask-SQLAlchemy)

The database uses a relational model with 7 main tables supporting multi-tenant SaaS architecture with role-based access control.

DATABASE TABLES
===============

TABLE 1: ADMINS
---------------

Purpose: Stores system administrators who manage the entire platform

Table Name: admins

Fields:
- id: Integer, Primary Key, Auto Increment
  Description: Unique identifier for each admin record

- email: String(255), Unique, Not Null, Indexed
  Description: Admin email address, must be unique across all admins

- password: String(255), Not Null
  Description: Hashed password using bcrypt algorithm

- name: String(255), Not Null
  Description: Admin full name

- is_active: Boolean, Default True, Not Null
  Description: Whether admin account is active or deactivated

- created_at: DateTime, Not Null, Default Current Timestamp
  Description: Record creation timestamp

- updated_at: DateTime, Not Null, Auto Update on Change
  Description: Last update timestamp

Relationships: None (standalone table, top-level entity)

Constraints:
- Primary Key: id
- Unique: email
- Index: email

TABLE 2: TENANTS
----------------

Purpose: Stores organizations or businesses using the platform

Table Name: tenants

Fields:
- id: Integer, Primary Key, Auto Increment
  Description: Unique identifier for each tenant

- name: String(255), Not Null
  Description: Company or organization name

- slug: String(255), Unique, Not Null, Indexed
  Description: URL-friendly identifier like company-name, used for SEO and routing

- email: String(255), Unique, Not Null, Indexed
  Description: Company email address, must be unique

- phone: String(20), Nullable
  Description: Company phone number

- business_metadata: JSON, Nullable, Default Empty Object
  Description: Flexible storage for business information including GST number, PAN number, address, and other metadata

- admin_name: String(255), Not Null
  Description: Name of the tenant administrator

- admin_email: String(255), Unique, Not Null, Indexed
  Description: Tenant administrator email, must be unique across all tenants

- admin_password: String(255), Not Null
  Description: Tenant administrator password, hashed using bcrypt

- is_active: Boolean, Default True, Not Null
  Description: Whether tenant account is active

- subscription_status: String(50), Default trial, Not Null
  Description: Subscription status values: trial, active, suspended, cancelled

- created_at: DateTime, Not Null, Default Current Timestamp
  Description: Record creation timestamp

- updated_at: DateTime, Not Null, Auto Update on Change
  Description: Last update timestamp

Relationships:
- Has many Users (one-to-many)
- Has many Tests (one-to-many)
- Has many AccessMatrix entries (one-to-many)

Constraints:
- Primary Key: id
- Unique: slug, email, admin_email
- Index: slug, email, admin_email

TABLE 3: USERS
--------------

Purpose: Stores all end users including employees, managers, and regular users

Table Name: users

Fields:
- id: Integer, Primary Key, Auto Increment
  Description: Unique identifier for each user

- tenant_id: Integer, Foreign Key to tenants.id, Not Null, Indexed, Cascade Delete
  Description: Reference to tenant this user belongs to

- name: String(255), Not Null
  Description: User full name

- email: String(255), Not Null, Indexed
  Description: User email address, unique within tenant scope

- phone: String(20), Nullable
  Description: User phone number

- password: String(255), Not Null
  Description: User password, hashed using bcrypt

- profile_data: JSON, Nullable, Default Empty Object
  Description: Flexible storage for user profile information like age, gender, preferences, custom fields

- role: String(50), Default user, Not Null
  Description: User role values: user, employee, manager, sales_rep

- access_level: String(50), Default basic, Not Null
  Description: Access level values: basic, premium, admin

- is_active: Boolean, Default True, Not Null
  Description: Whether user account is active

- is_verified: Boolean, Default False, Not Null
  Description: Whether user email is verified

- temp_password: String(255), Nullable
  Description: Temporary password for employee onboarding

- password_reset_required: Boolean, Default False, Not Null
  Description: Flag indicating if password reset is required on first login

- last_login: DateTime, Nullable
  Description: Last login timestamp

- created_at: DateTime, Not Null, Default Current Timestamp
  Description: Record creation timestamp

- updated_at: DateTime, Not Null, Auto Update on Change
  Description: Last update timestamp

Relationships:
- Belongs to one Tenant (many-to-one via tenant_id)
- Has many TestResponses (one-to-many)

Constraints:
- Primary Key: id
- Foreign Key: tenant_id references tenants(id) ON DELETE CASCADE
- Unique: Combination of tenant_id and email must be unique
- Index: tenant_id, email

TABLE 4: TESTS
--------------

Purpose: Stores test and questionnaire definitions

Table Name: tests

Fields:
- id: Integer, Primary Key, Auto Increment
  Description: Unique identifier for each test

- tenant_id: Integer, Foreign Key to tenants.id, Not Null, Indexed, Cascade Delete
  Description: Reference to tenant that owns this test

- title: String(255), Not Null
  Description: Test title or name

- description: Text, Nullable
  Description: Test description or instructions

- is_active: Boolean, Default True, Not Null
  Description: Whether test is currently active and available

- created_at: DateTime, Not Null, Default Current Timestamp
  Description: Record creation timestamp

- updated_at: DateTime, Not Null, Auto Update on Change
  Description: Last update timestamp

Relationships:
- Belongs to one Tenant (many-to-one via tenant_id)
- Has many Questions (one-to-many)
- Has many TestResponses (one-to-many)

Constraints:
- Primary Key: id
- Foreign Key: tenant_id references tenants(id) ON DELETE CASCADE
- Index: tenant_id

TABLE 5: QUESTIONS
------------------

Purpose: Stores individual questions within tests

Table Name: questions

Fields:
- id: Integer, Primary Key, Auto Increment
  Description: Unique identifier for each question

- test_id: Integer, Foreign Key to tests.id, Not Null, Indexed, Cascade Delete
  Description: Reference to test this question belongs to

- question_text: Text, Not Null
  Description: The actual question text

- question_type: String(50), Not Null
  Description: Question type values: text, radio, checkbox, range, textarea

- section: String(100), Nullable
  Description: Section name like Section A, Section B for grouping questions

- options: JSON, Nullable
  Description: Array of answer options for radio and checkbox question types

- default_order: Integer, Not Null
  Description: Original order when question was created

- priority_order: Integer, Not Null
  Description: Current display order, can be modified by users

- is_required: Boolean, Default True, Not Null
  Description: Whether question must be answered

- placeholder: String(255), Nullable
  Description: Placeholder text for input fields

- created_at: DateTime, Not Null, Default Current Timestamp
  Description: Record creation timestamp

- updated_at: DateTime, Not Null, Auto Update on Change
  Description: Last update timestamp

Relationships:
- Belongs to one Test (many-to-one via test_id)

Constraints:
- Primary Key: id
- Foreign Key: test_id references tests(id) ON DELETE CASCADE
- Index: test_id

TABLE 6: TEST_RESPONSES
-----------------------

Purpose: Stores user answers to tests

Table Name: test_responses

Fields:
- id: Integer, Primary Key, Auto Increment
  Description: Unique identifier for each test response

- test_id: Integer, Foreign Key to tests.id, Not Null, Indexed, Cascade Delete
  Description: Reference to test that was taken

- user_id: Integer, Foreign Key to users.id, Not Null, Indexed, Cascade Delete
  Description: Reference to user who took the test

- responses: JSON, Not Null, Default Empty Object
  Description: Dictionary storing answers in format {question_id: answer}

- image_path: String(500), Nullable
  Description: File system path to uploaded image file

- image_url: String(500), Nullable
  Description: URL to access uploaded image through API

- is_completed: Boolean, Default False, Not Null
  Description: Whether test submission is completed

- started_at: DateTime, Not Null, Default Current Timestamp
  Description: When user started the test

- completed_at: DateTime, Nullable
  Description: When user completed the test

- created_at: DateTime, Not Null, Default Current Timestamp
  Description: Record creation timestamp

- updated_at: DateTime, Not Null, Auto Update on Change
  Description: Last update timestamp

Relationships:
- Belongs to one Test (many-to-one via test_id)
- Belongs to one User (many-to-one via user_id)

Constraints:
- Primary Key: id
- Foreign Key: test_id references tests(id) ON DELETE CASCADE
- Foreign Key: user_id references users(id) ON DELETE CASCADE
- Index: test_id, user_id

TABLE 7: ACCESS_MATRIX
----------------------

Purpose: Defines permissions for each role using Role-Based Access Control

Table Name: access_matrix

Fields:
- id: Integer, Primary Key, Auto Increment
  Description: Unique identifier for each access matrix entry

- tenant_id: Integer, Foreign Key to tenants.id, Nullable, Indexed, Cascade Delete
  Description: Reference to tenant for tenant-specific permissions, null for global permissions

- role: String(50), Not Null, Indexed
  Description: Role name values: super_admin, tenant_admin, manager, employee, user

- permissions: JSON, Not Null, Default Empty Object
  Description: Dictionary defining permissions format: {resource: [action1, action2]}
  Example: {employees: [create, read, update, delete], tests: [read]}

- description: Text, Nullable
  Description: Description of the role permissions

- is_active: Boolean, Default True, Not Null
  Description: Whether this permission set is active

- created_at: DateTime, Not Null, Default Current Timestamp
  Description: Record creation timestamp

- updated_at: DateTime, Not Null, Auto Update on Change
  Description: Last update timestamp

Relationships:
- Belongs to one Tenant (optional, many-to-one via tenant_id, null for global permissions)

Constraints:
- Primary Key: id
- Foreign Key: tenant_id references tenants(id) ON DELETE CASCADE
- Unique: Combination of tenant_id and role must be unique
- Index: tenant_id, role

DATABASE RELATIONSHIPS DIAGRAM
===============================

Relationship Hierarchy:

Admins
  (Standalone table, no relationships)

Tenants
  |
  |--- Users (one tenant has many users)
  |      |
  |      |--- TestResponses (one user has many responses)
  |
  |--- Tests (one tenant has many tests)
  |      |
  |      |--- Questions (one test has many questions)
  |      |
  |      |--- TestResponses (one test has many responses)
  |
  |--- AccessMatrix (one tenant has many permission sets)

Relationship Types:

1. One-to-Many Relationships:
   - Tenant to Users
   - Tenant to Tests
   - Tenant to AccessMatrix
   - Test to Questions
   - Test to TestResponses
   - User to TestResponses

2. Many-to-One Relationships:
   - Users to Tenant
   - Tests to Tenant
   - Questions to Test
   - TestResponses to Test
   - TestResponses to User
   - AccessMatrix to Tenant (optional)

3. No Relationships:
   - Admins (standalone entity)

CASCADE DELETION RULES
======================

When a parent record is deleted, child records are automatically deleted:

1. If Tenant is deleted:
   - All Users belonging to that tenant are deleted
   - All Tests belonging to that tenant are deleted
   - All AccessMatrix entries for that tenant are deleted
   - All TestResponses are deleted (through Users and Tests cascade)

2. If Test is deleted:
   - All Questions belonging to that test are deleted
   - All TestResponses for that test are deleted

3. If User is deleted:
   - All TestResponses by that user are deleted

4. If AccessMatrix entry is deleted:
   - No cascading (standalone deletion)

This ensures data consistency and prevents orphaned records.

MULTI-TENANCY ARCHITECTURE
===========================

Data Isolation Strategy:
- Each tenant has completely isolated data
- All tenant-related tables include tenant_id foreign key
- Users can only access data from their own tenant
- Database queries are scoped by tenant_id
- Unique constraints apply within tenant scope where applicable

Tenant Scoping:
- Users table: email unique within tenant, not globally
- Tests table: scoped to tenant
- TestResponses: scoped through user and test to tenant
- AccessMatrix: can be global (tenant_id null) or tenant-specific

Data Access Pattern:
- All queries filter by tenant_id
- JWT token includes tenant_id for authorization
- Backend enforces tenant isolation at API level

ROLE-BASED ACCESS CONTROL (RBAC)
=================================

Permission Model:
- Permissions stored in AccessMatrix table as JSON
- Format: {resource: [action1, action2, action3]}
- Resources: employees, users, tests, reports, tenants
- Actions: create, read, update, delete, all

Roles:
1. super_admin: Full system access, can manage all tenants
2. tenant_admin: Full access to their tenant, can manage users and tests
3. manager: Limited access, can manage employees but not delete them
4. employee: Basic access, can view and update own data
5. user: Limited access, can only take tests and view own profile

Permission Checking:
- Backend checks permissions before allowing operations
- Permission decorators validate access at route level
- Tenant-specific permissions override global permissions
- super_admin and tenant_admin have implicit full access

JSON FIELD USAGE
================

JSON fields provide flexible storage for dynamic data:

1. business_metadata (Tenants table):
   Stores tenant business information like:
   - GST number
   - PAN number
   - Address details
   - Additional custom fields

2. profile_data (Users table):
   Stores user profile information like:
   - Age
   - Gender
   - Preferences
   - Custom profile fields

3. options (Questions table):
   Stores answer options array for radio and checkbox questions:
   Example: [Option 1, Option 2, Option 3, Option 4]

4. responses (TestResponses table):
   Stores user answers as dictionary:
   Format: {question_id: answer_value}
   Example: {1: Yes, 2: [Option A, Option C], 3: Some text answer}

5. permissions (AccessMatrix table):
   Stores permission definitions as dictionary:
   Format: {resource: [action1, action2]}
   Example: {employees: [create, read, update], tests: [read]}

INDEXES AND PERFORMANCE
========================

Primary Indexes (Primary Keys):
- All tables have id as primary key with auto increment

Unique Indexes:
- admins.email
- tenants.slug
- tenants.email
- tenants.admin_email
- users combination of tenant_id and email
- access_matrix combination of tenant_id and role

Foreign Key Indexes:
- users.tenant_id
- tests.tenant_id
- questions.test_id
- test_responses.test_id
- test_responses.user_id
- access_matrix.tenant_id

Lookup Indexes:
- users.email (for login queries)
- access_matrix.role (for permission queries)

These indexes ensure fast queries and enforce data integrity.

DATA FLOW EXAMPLES
==================

FLOW 1: USER REGISTRATION AND LOGIN
------------------------------------

Step 1: User Registration
- Frontend sends POST /api/user/register with tenant_id, name, email, password
- Backend validates email format and password strength
- Backend checks if email already exists for that tenant
- Backend creates new User record in users table
- tenant_id stored to link user to tenant
- password hashed using bcrypt before storage
- profile_data initialized as empty JSON object
- Backend returns JWT token with user_id and tenant_id

Step 2: User Login
- Frontend sends POST /api/user/login with email and password
- Backend queries users table filtering by email and tenant_id
- Backend verifies password using bcrypt
- Backend updates last_login timestamp in users table
- Backend creates JWT token with user_id, tenant_id, role
- Backend returns token and user data to frontend

FLOW 2: TEST CREATION AND TAKING
---------------------------------

Step 1: Tenant Creates Test
- Tenant admin sends POST /api/test/tests with title and description
- Backend gets tenant_id from JWT token
- Backend creates new Test record in tests table
- tenant_id stored to link test to tenant
- is_active set to True by default
- Backend returns test details with test_id

Step 2: Tenant Adds Questions
- Tenant admin sends POST /api/test/tests/{test_id}/questions
- Backend validates test exists and belongs to tenant
- Backend creates Question records in questions table
- test_id stored to link question to test
- options stored as JSON array if question_type is radio or checkbox
- priority_order determines display order
- Backend returns question details

Step 3: User Starts Test
- User sends POST /api/test/tests/{test_id}/start
- Backend gets user_id and tenant_id from JWT token
- Backend verifies test belongs to user tenant
- Backend creates TestResponse record in test_responses table
- test_id and user_id stored
- responses initialized as empty JSON object
- is_completed set to False
- started_at set to current timestamp
- Backend returns test questions ordered by priority_order

Step 4: User Submits Answers
- User sends POST /api/test/responses/{response_id}/answers
- Backend gets user_id from JWT token
- Backend verifies response belongs to user
- Backend updates responses JSON field: {question_id: answer}
- Multiple submissions update the same response record
- Backend returns updated response

Step 5: User Completes Test
- User sends POST /api/test/responses/{response_id}/complete
- Backend sets is_completed to True
- Backend sets completed_at to current timestamp
- All answers stored in responses JSON field
- Backend returns completed response

FLOW 3: EMPLOYEE MANAGEMENT WITH RBAC
--------------------------------------

Step 1: Tenant Creates Employee
- Tenant admin sends POST /api/tenant/employees with name and email
- Backend gets tenant_id from JWT token
- Backend checks permission: employees create
- Backend generates temporary password
- Backend creates User record in users table
- tenant_id stored
- role set to employee
- temp_password stored (plain text, sent via email)
- password_reset_required set to True
- password field stores hashed temp_password
- Backend returns employee data with temp_password

Step 2: Employee First Login
- Employee sends POST /api/user/login with email and temp_password
- Backend verifies temp_password matches
- Backend returns password_reset_required flag
- Frontend shows password reset form

Step 3: Employee Resets Password
- Employee sends POST /api/user/reset-password
- Backend verifies temp_password
- Backend validates new password strength
- Backend updates password field with hashed new password
- Backend clears temp_password field
- Backend sets password_reset_required to False
- Backend returns new JWT token
- Employee can now use new password for future logins

FLOW 4: ACCESS CONTROL CHECK
-----------------------------

Step 1: User Attempts Action
- User with manager role tries to delete employee
- Frontend sends DELETE /api/tenant/employees/{employee_id}
- Backend extracts role from JWT token: manager
- Backend gets tenant_id from JWT token

Step 2: Permission Check
- Backend queries AccessMatrix table
- Filters by tenant_id and role: manager
- Retrieves permissions JSON: {employees: [read, update]}
- Backend checks if delete action exists in employees permissions
- Delete action not found in permissions

Step 3: Access Denied
- Backend returns 403 Forbidden error
- Error message: Access denied. manager does not have delete permission for employees
- Frontend displays error message to user

STORAGE LOCATIONS
=================

Database Storage (PostgreSQL):
- All structured data stored in PostgreSQL tables
- Database runs in Docker container
- Data persisted in Docker volume: postgres_data
- All relationships, constraints, and indexes managed by PostgreSQL

File System Storage:
- Uploaded images stored in: backend/uploads/test_images/
- Image filename format: {response_id}_{timestamp}_{original_filename}
- Image paths stored in test_responses.image_path field
- Image URLs stored in test_responses.image_url field
- Images served through GET /api/test/uploads/{filename} endpoint

TIMESTAMP TRACKING
==================

All tables include timestamp fields for auditing:

created_at:
- Set automatically when record is created
- Default value: Current UTC timestamp
- Never changes after creation
- Used for tracking when record was first created

updated_at:
- Set automatically when record is created
- Updates automatically whenever record is modified
- Default value: Current UTC timestamp
- Used for tracking last modification time

last_login (Users table):
- Updated when user successfully logs in
- Initially null
- Used for tracking user activity

started_at (TestResponses table):
- Set when user starts a test
- Default value: Current UTC timestamp
- Never changes after creation
- Used for tracking when test was started

completed_at (TestResponses table):
- Set when user completes a test
- Initially null
- Updated when is_completed changes to True
- Used for tracking when test was completed

DATA INTEGRITY RULES
====================

1. Foreign Key Constraints:
   - Ensure all foreign keys reference valid parent records
   - Prevent orphaned records
   - Cascade deletions maintain referential integrity

2. Unique Constraints:
   - Prevent duplicate emails within scope
   - Prevent duplicate slugs for tenants
   - Prevent duplicate role definitions per tenant

3. Not Null Constraints:
   - Ensure required fields always have values
   - Prevent incomplete records

4. Check Constraints (Implicit):
   - Email format validated at application level
   - Password strength validated at application level
   - Role values validated at application level

5. Default Values:
   - Ensure sensible defaults for optional fields
   - is_active defaults to True
   - subscription_status defaults to trial
   - role defaults to user
   - access_level defaults to basic

SUMMARY
=======

The database architecture supports a multi-tenant SaaS platform with:

- Complete data isolation between tenants
- Role-based access control with flexible permissions
- Hierarchical relationships between entities
- Cascade deletion for data consistency
- Flexible JSON fields for dynamic data
- Comprehensive timestamp tracking
- Indexes for optimal query performance
- Foreign key constraints for data integrity

All data flows through well-defined relationships ensuring consistency, security, and scalability.

