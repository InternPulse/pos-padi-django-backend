![image](https://github.com/user-attachments/assets/3ec0f633-1414-4086-a8f4-42649e27003f)
---
# POS Padi Django Backend API

## Project Overview

**POS-Padi – POS Transaction Management System**

POS-Padi is a Django-based POS transaction management app that leverages the Django REST Framework, built-in authentication, and JWT for secure API authentication. It provides a structured API with endpoints across multiple apps:

- **Users** – User registration, login, and JWT-based authentication.
- **Companies** – Company creation, Agent registration and performance evaluation.
- **Agents** – Agent onboarding and account management.
- **Customers** – Customer tracking and loyalty rewards system.

POS-Padi is a robust API to help POS agents and business owners efficiently manage their operations. The platform addresses issues such as fraud, transaction disputes, and cash shortages by offering real-time insights, financial tools, and smart alerts. This API contains User Authentication, Company Sign up, Agent Onboarding and Customer Registration

## Live Link

[API Live Demo](https://pos-padi-django-backend.onrender.com/)

## Documentation Link

Postman API Documentation [here](https://documenter.getpostman.com/view/43614350/2sB2ixjZkQ).

---

## Installation Instructions

### Prerequisites

Ensure the following tools are installed:

- Python (>= 3.9 recommended)
- pip (Python package manager)
- Git
- Virtual environment tool (e.g., `venv` or `virtualenv`)
- MySQL

### How to Run the API Locally

1. **Clone the repository:**

    ```bash
    git clone https://github.com/InternPulse/pos-padi-django-backend.git
    cd pos-padi-django-backend
    ```

2. **Set up a virtual environment:**

   **Windows:**

    ```bash

    python -m venv .venv
    .\.venv\Scripts\activate
    ```

   **macOS/Linux:**

    ```bash
    
    python -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database:**

    ```bash
    python manage.py migrate
    ```

5. **Create a superuser**

    ```bash
    python manage.py createsuperuser
    ```

6. **Start the server:**

    ```bash
    python manage.py runserver
    ```

   The API will be available at `http://127.0.0.1:8000`.

---

## Features

- **Advanced Analytics:** Provides insights into key performance metrics.
- **REST API:** Enables querying and managing analytics data.
- **Filters:** Supports filtering by dates, products, and profitability.
- **Data Aggregation:** Converts raw data into actionable insights.
- **Reporting:** Offers downloadable and visual reports.

---

## Usage

- Access the API locally at `http://127.0.0.1:8000/`.
- Test endpoints using tools like Postman, cURL, or other API testing utilities.
- Refer to the [API Documentation](https://documenter.getpostman.com/view/43614350/2sB2ixjZkQ) for detailed instructions.

---

## API Endpoints

**Base URL:** `http://127.0.0.1:8000/api/v1/`

| Endpoint                                    | Method | Description                           |
|---------------------------------------------|--------|---------------------------------------|
| `/users/register/`                          | POST   | Register an owner.                    |
| `/users/verify/`                            | POST   | Owner email verification.             |
| `/companies/`                               | POST   | Register a company.                   |
| `/agents`                                   | POST   | Sign up an agent.                     |
| `/companies/dashboard/?start_date=<string>&end_date=<string>&agent_id=<string>/`| GET    | Fetch a aggregation relevant metrics. |
| `/users/summary`                            | GET    | Fetch a summary of all data linked to a user.|

For a comprehensive list, refer to the [API Documentation](https://documenter.getpostman.com/view/43614350/2sB2ixjZkQ).

---

## Project Structure

```plaintext
pos-padi-django-backend/
├── manage.py                     # Django command-line utility
├── apps/                         # Django apps
│   ├── common/                   # Shared utilities/models
│   ├── agents/                   # Agents-related logic
│   ├── companies/                # Company management
│   ├── customers/                # Customer management
│   ├── external_tables/          # External data integrations
│   └── users/                    # User authentication & profiles
│
├── config/                       # Project configuration
│   └── settings/                 # Django settings (split by environment)
│       ├── base.py               # Base settings (shared)
│       ├── test.py               # Test-specific settings
│       ├── local.py              # Local development settings
│       └── prod.py               # Production settings
│
...  
```

---

## Environment Variables

Create a `.env` file in the root directory with the following keys:

```bash
DEFAULT_SECRET_KEY=your-secret-key
DJANGO_SECRET_KEY=your_prod_secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# MySQL
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PORT=your_db_port
DB_PASSWORD=your_db_passsword
DB_NAME=your_db_name
DB_CA_CERT_PATH=your_db_CA_cert_path(if applicable)

# Django SMTP
EMAIL_HOST=your_email_host
EMAIL_PORT=your_email_port
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email_host_user
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=your_defualt_sending_email

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# CORS
CORS_ALLOWED_ORIGINS=http://localhost
```

---

## Contributions

Contributions are welcome! If you’re interested:

1. Create an issue or comment on the repository to let others know what you're working on to avoid overlapping efforts.
2. Follow the steps outlined below to contribute.

### Contribution Guidelines

1. **Clone the repository:**

    ```bash
    git clone https://github.com/InternPulse/pos-padi-django-backend.git
    ```

2. **Set the origin branch:**

    ```bash
    git remote add origin https://github.com/InternPulse/pos-padi-django-backend.git
    git pull origin dev
    ```

3. **Create a new branch for your task:**

    ```bash
    git checkout -b BA-001/Feat/Sign-Up-Form
    ```

4. **Make your changes and commit:**

    ```bash
    git add .
    git commit -m "your commit message"
    ```

5. **Sync with the dev branch to avoid conflicts:**

    ```bash
    git pull origin dev
    ```

6. **Push your branch:**

    ```bash
    git push -u origin BA-001/Feat/Sign-Up-Form
    ```

7. **Create a pull request to the dev branch.** Ensure the PR description is clear and includes test instructions.

---

## Commit Standards and Guidelines

### Commit Cheat Sheet

| Type      | Description                                  |
|-----------|----------------------------------------------|
| `feat`    | Features: A new feature                     |
| `fix`     | Bug Fixes: A bug fix                        |
| `docs`    | Documentation: Documentation-only changes   |
| `style`   | Styles: Formatting or cosmetic changes      |
| `refactor`| Code Refactoring: Neither fixes a bug nor adds a feature |
| `perf`    | Performance: Optimizes performance          |
| `test`    | Tests: Adding or updating tests             |
| `build`   | Builds: Changes to build tools or dependencies |
| `ci`      | CI: Updates to CI configurations            |
| `chore`   | Chores: Maintenance or configuration tasks  |
| `revert`  | Reverts: Reverts a previous commit          |

### Sample Commit Messages

- `chore: Update README file – Maintenance task.`
- `feat: Add user registration endpoint – New feature added.`

---

## License

This project is licensed under the MIT License.
