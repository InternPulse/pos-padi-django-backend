 # POS Padi Django Backend API

## Project Overview

**PedMonie – Payment Integration App**  

PedMonie is a Django-based payment integration app that leverages the Django REST Framework, built-in authentication, and JWT for secure API authentication. It provides a structured API with endpoints across multiple apps:  

- **Authentication** – User registration, login, and JWT-based authentication.  
- **Dashboard** – User and admin dashboards for transaction insights.  
- **Orders** – Order creation, tracking, and management.  
- **Payments** – Payment processing, transaction history, and status tracking.  
- **Support** – Customer support ticketing and inquiry handling.  
- **Wallets** – Digital wallet management, fund transfers, and balance tracking.  

PedMonie ensures seamless payment handling with secure authentication and robust API endpoints for a smooth financial experience.


Features Implemented

    Financial Reporting: Profit and loss reports, daily reports, and net profit calculations with filtering by date range, terminal, and agent.
    Transaction Management: CRUD operations for transactions (create, edit, delete) with audit logging, integrated with a Node.js transaction API.
    Export Functionality: Reports exportable in PDF and Excel formats.

    
## Live Link

[API Live Demo](https://)

## Documentation Link

Postman API Documentation [here](https://documenter.getpostman.com/view/41687429/2sAYdZttrw).

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
    cd pedmonie-django-backend
    ```

2. **Set up a virtual environment:**

    **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

    **macOS/Linux:**
    ```bash
    python -m venv venv
    source venv/bin/activate
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
- Refer to the [API Documentation](https://documenter.getpostman.com/view/36548151/2sAYBPmZm1) for detailed instructions.

---


### API Endpoints
**Base URL**: `http://127.0.0.1:8000/api/v1/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/users/profit_loss_report/` | GET | Fetch profit and loss report (owners only). Supports `start_date`, `end_date`, `terminal`, `agent`, and `export` (pdf/excel) query params. |
| `/users/daily_report/` | GET | Fetch daily report for a specific date. Supports `date`, `agent`, and `terminal` query params. |
| `/users/net_profit/` | GET | Fetch net profit for a date range. Supports `start_date` and `end_date` query params. |
| `/transactions/` | GET, POST | List or create transactions via Node.js API. |
| `/transactions/<id>/` | PUT, DELETE | Update or delete a transaction via Node.js API, with audit logging. |



## API Endpoints

**Base URL:** `http://127.0.0.1:8000/api/v1/`

| Endpoint                                    | Method | Description                           |
|---------------------------------------------|--------|---------------------------------------|
| `/financial/analytics/`                     | GET    | Fetch all financial analytics records.|
| `/financial/analytics/top_products/`        | GET    | Get top products by profitability.    |
| `/financial/analytics/?year=2022`           | GET    | Filter analytics by year.             |
| `/financial/analytics/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | GET | Filter analytics by date range.       |
| `/financial/analytics/profit_records/`      | GET    | Fetch records with profit only.       |
| `/financial/analytics/selling_at_loss/`     | GET    | Fetch records with losses only.       |

For a comprehensive list, refer to the [API Documentation](https://documenter.getpostman.com/view/36548151/2sAYBPmZm1).

---

## Project Structure

```plaintext
pos-padi-django-backend/
├── analytics_service/
│   ├── sales_performance/      # Sales Performance Analytics
│   ├── product_performance/    # Product Performance Analytics
│   ├── marketing_conversion/   # Marketing Analytics
│   ├── profitability_financial/ # Financial Analytics
│   ├── shared/                 # Shared utilities and helpers
├── manage.py                   # Django entry point
├── requirements.txt            # Python dependencies
└── ...
```

---

## Environment Variables

Create a `.env` file in the root directory with the following keys:

```bash
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
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
