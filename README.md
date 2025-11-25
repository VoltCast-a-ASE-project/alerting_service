# VoltCast Notification & Alerting Service

This service is a Python-based microservice designed for the VoltCast system. It provides a standalone solution for managing user-defined alert rules and triggering notifications when incoming data breaches those rules.

The service is built with FastAPI for high performance, SQLAlchemy for ORM, and Pydantic for data validation. It uses a PostgreSQL database for data persistence.

## Setup

Follow these steps to set up and run the service locally.

### 1. Prerequisites
- Python 3.11+
- A running PostgreSQL database instance.

### 2. Clone the Repository
```bash
git clone <your-repository-url>
cd alerting_service
```

### 3. Create a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Configure Database
The service connects to PostgreSQL using a database URL. You must set the `DATABASE_URL` environment variable before running the application.

Create a `.env` file in the root of the project directory:

```
DATABASE_URL="postgresql://user:password@hostname:port/database_name"
```

Replace `user`, `password`, `hostname`, `port`, and `database_name` with your actual PostgreSQL connection details. The application will automatically load this variable.

## Running the Service

Once the setup is complete, you can run the FastAPI application using `uvicorn`. The application will automatically create the necessary `alert_rules` table in your database on startup.

```bash
uvicorn main:app --reload
```
- `--reload`: Enables auto-reloading, which is useful for development. The server will restart automatically after code changes.

The service will be available at `http://127.0.0.1:8000`.

## API Endpoints

You can access the interactive API documentation (Swagger UI) by navigating to `http://127.0.0.1:8000/docs`.

### Alert Rule Management

*   **Create a new rule**
    *   **Endpoint:** `POST /api/v1/rules`
    *   **Body:**
        ```json
        {
          "user_id": "user-123",
          "metric_type": "PV_PRODUCTION",
          "threshold_value": 1000.5,
          "condition": "GREATER_THAN",
          "is_active": true,
          "delivery_channel": "EMAIL"
        }
        ```

*   **Retrieve all active rules for a user**
    *   **Endpoint:** `GET /api/v1/rules/{user_id}`

*   **Deactivate/delete a rule**
    *   **Endpoint:** `DELETE /api/v1/rules/{rule_id}`


### Data Ingestion

*   **Ingest new data for evaluation**
    *   **Endpoint:** `POST /api/v1/data/ingest`
    *   **Description:** This endpoint asynchronously evaluates incoming data against all active rules for the specified user and metric. If a rule's condition is met, a mock alert is logged to the console.
    *   **Body:**
        ```json
        {
          "user_id": "user-123",
          "metric_type": "PV_PRODUCTION",
          "value": 1100.0,
          "timestamp": "2025-11-24T10:00:00Z"
        }
        ```
    *   **Example Log Output (on violation):**
        ```
        [ALERT TRIGGERED for User user-123]: PV_PRODUCTION (1100.0) violated rule (Condition: GREATER_THAN 1000.5) via Channel: EMAIL
        ```
