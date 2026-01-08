# VoltCast Notification & Alerting Service

This service is a Python-based microservice designed for the VoltCast system. It provides a standalone solution for managing user-defined alert rules and triggering notifications when incoming data breaches those rules.

The service is built with **FastAPI** for high performance, **SQLAlchemy** for ORM, and **Pydantic** for data validation. It uses a **SQLite** database for easy local development and persistence (configured via Docker volume). It also integrates with **Resend** for sending email notifications.

## Features

*   **Rule Management**: Create, list, and delete alert rules via API.
*   **Real-time Polling**: Automatically polls Kostal and Fronius services for real-time data.
*   **Alerting**: Triggers email alerts via Resend when thresholds are breached.
*   **Data Ingestion**: Manual data ingestion endpoint for testing and simulation.

## Setup

You can run the service using Docker (recommended) or locally with Python.

### Prerequisites

*   **Docker** & **Docker Compose** (Recommended)
*   **Python 3.10+** (If running locally)
*   **Resend API Key**: Required for sending email alerts. [Get one here](https://resend.com).

### Configuration (`.env`)

Whether running with Docker or locally, you can configure the service using environment variables. Create a `.env` file in the root directory (or use the one provided in `docker-compose.yml` environment section):

| Variable | Description | Default |
| :--- | :--- | :--- |
| `RESEND_API_KEY` | **Required**. Your Resend API Key for emails. | None |
| `DATABASE_URL` | Database connection string. | `sqlite:////app/data/alerting.db` (Docker) |
| `KOSTAL_SERVICE_URL` | URL to poll Kostal data from. | `http://kostal-ms:8082/kostal/realtimedata` |
| `FRONIUS_SERVICE_URL` | URL to poll Fronius data from. | `http://fronius-ms:8081/fronius/realtimedata` |

---

### Option 1: Running with Docker (Recommended)

The easiest way to run the service is using Docker Compose.

1.  **Configure Environment**:
    Open `docker-compose.yml` and ensure your `RESEND_API_KEY` is set (or pass it from your shell).

2.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```

The service will start on port **8087**.
*   **API URL**: `http://localhost:8087`
*   **Docs**: `http://localhost:8087/docs`

### Option 2: Running Locally

1.  **Clone the Repository**:
    ```bash
    git clone <your-repository-url>
    cd alerting_service
    ```

2.  **Create Virtual Environment**:
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables**:
    Create a `.env` file or export them in your shell:
    ```bash
    # Windows (PowerShell)
    $env:RESEND_API_KEY="your_api_key"
    
    # macOS/Linux
    export RESEND_API_KEY="your_api_key"
    ```

5.  **Run the Service**:
    ```bash
    uvicorn main:app --reload --port 8087
    ```

Access the service at `http://127.0.0.1:8087`.

---

## API Endpoints

Interactive API documentation is available at `/docs`.

### Alert Rule Management

*   **Create a new rule**
    *   **Endpoint:** `POST /alert/api/v1/rules`
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
    *   **Endpoint:** `GET /alert/api/v1/rules/{user_id}`

*   **Deactivate/delete a rule**
    *   **Endpoint:** `DELETE /alert/api/v1/rules/{rule_id}`

### Data Ingestion (Manual)

*   **Ingest new data for evaluation**
    *   **Endpoint:** `POST /alert/api/v1/data/ingest`
    *   **Body:**
        ```json
        {
          "user_id": "user-123",
          "metric_type": "PV_PRODUCTION",
          "value": 1100.0,
          "timestamp": "2025-11-24T10:00:00Z"
        }
        ```

### Health Check

*   **Check service status**
    *   **Endpoint:** `GET /alert/hello`
