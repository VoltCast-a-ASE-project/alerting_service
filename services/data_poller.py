import asyncio
import httpx
import os
import logging

logger = logging.getLogger("uvicorn.info")

# Default URLs (can be overridden by env vars)
KOSTAL_REALTIME_URL = os.getenv("KOSTAL_SERVICE_URL", "http://kostal-ms:8082/kostal/realtimedata")
FRONIUS_REALTIME_URL = os.getenv("FRONIUS_SERVICE_URL", "http://fronius-ms:8081/fronius/realtimedata")

async def fetch_data(client, url, service_name):
    try:
        logger.info(f"Polling {service_name} at {url}...")
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched {service_name} data: {str(data)[:200]}...")
        return data
    except httpx.RequestError as e:
        logger.error(f"Network error polling {service_name}: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error polling {service_name}: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error polling {service_name}: {e}")
    return None

async def poll_data_services():
    """
    Constantly queries the Kostal and Fronius services for real-time data.
    """
    async with httpx.AsyncClient() as client:
        while True:
            await asyncio.gather(
                fetch_data(client, KOSTAL_REALTIME_URL, "Kostal"),
                fetch_data(client, FRONIUS_REALTIME_URL, "Fronius")
            )
            
            # Wait for 60 seconds before next poll
            await asyncio.sleep(60)
