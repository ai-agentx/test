"""Currency exchange tool for LangGraph agent using Frankfurter API."""

import logging
import httpx
from langchain_core.tools import tool
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)


@tool
def get_exchange_rate(
    currency_from: str = "USD",
    currency_to: str = "EUR",
    currency_date: str = "latest",
    amount: float = 1.0
) -> Union[str, Dict[str, Any]]:
    """Get current exchange rate and convert currency using Frankfurter API.

    This tool fetches real-time exchange rates and can convert amounts between currencies.

    Args:
        currency_from: The currency to convert from (e.g., "USD", "EUR", "GBP").
        currency_to: The currency to convert to (e.g., "EUR", "USD", "JPY").
        currency_date: The date for the exchange rate or "latest" for current rates.
        amount: The amount to convert (defaults to 1.0 for rate lookup).

    Returns:
        Dictionary containing exchange rate data and conversion result, or error message.
    """
    try:
        # Clean and validate inputs
        currency_from = currency_from.upper().strip()
        currency_to = currency_to.upper().strip()

        if not currency_from or not currency_to:
            return "Error: Currency codes cannot be empty"

        if currency_from == currency_to:
            return f"{amount} {currency_from} equals {amount} {currency_to} (same currency)"

        # Build API URL
        url = f"https://api.frankfurter.app/{currency_date}"
        params = {
            "from": currency_from,
            "to": currency_to,
            "amount": amount
        }

        logger.info(f"Fetching exchange rate: {amount} {currency_from} to {currency_to}")

        # Make API request
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()

        data = response.json()

        # Validate response format
        if "rates" not in data:
            return "Error: Invalid API response format - missing rates data"

        if currency_to not in data["rates"]:
            return f"Error: Currency {currency_to} not found in exchange rates"

        # Extract rate and converted amount
        rate = data["rates"][currency_to]
        converted_amount = data.get("amount", amount)

        # Format response
        if amount == 1.0:
            return f"Exchange rate: 1 {currency_from} = {rate} {currency_to}"
        else:
            return f"Currency conversion: {amount} {currency_from} = {converted_amount} {currency_to} (rate: 1 {currency_from} = {rate} {currency_to})"

    except httpx.HTTPError as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except httpx.TimeoutException:
        error_msg = "Request timeout - currency service unavailable"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except KeyError as e:
        error_msg = f"Invalid response data - missing key: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except ValueError as e:
        error_msg = f"Invalid amount value: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error during currency conversion: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
