"""Date helper utilities for OpenProject MCP Server and NanoClaw integration."""
from datetime import datetime, timedelta
from typing import Tuple, Optional
import re


def normalize_date_range(date_range: str, reference_date: Optional[datetime] = None) -> Tuple[str, str]:
    """Convert human-friendly date range strings to YYYY-MM-DD format.

    Supports multiple input formats:
    - "today" → today to today
    - "today to +N" → today to N days from today
    - "next week" → next Monday to next Sunday
    - "YYYY-MM-DD" → that date to that date
    - "YYYY-MM-DD to YYYY-MM-DD" → explicit date range

    Args:
        date_range: Human-friendly or explicit date range string
        reference_date: Reference date to use for "today" (defaults to datetime.now())

    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format

    Raises:
        ValueError: If date_range format is invalid or dates are malformed
    """
    if reference_date is None:
        reference_date = datetime.now()

    date_range = date_range.strip().lower()

    # Handle explicit date range: "YYYY-MM-DD to YYYY-MM-DD"
    if " to " in date_range:
        parts = date_range.split(" to ")
        if len(parts) == 2:
            start_part = parts[0].strip()
            end_part = parts[1].strip()

            # Check if it's a relative offset like "+N" or "+1"
            if end_part.startswith("+"):
                try:
                    offset_days = int(end_part[1:])
                    start_date = _parse_date_string(start_part, reference_date)
                    end_date = start_date + timedelta(days=offset_days)
                    return (
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d")
                    )
                except ValueError as e:
                    raise ValueError(f"Invalid offset format: {end_part}") from e

            # Both are explicit dates
            start_date = _parse_date_string(start_part, reference_date)
            end_date = _parse_date_string(end_part, reference_date)

            if end_date < start_date:
                raise ValueError(f"End date ({end_part}) cannot be before start date ({start_part})")

            return (
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )

    # Handle special keywords
    if date_range == "today":
        today = reference_date.strftime("%Y-%m-%d")
        return (today, today)

    if date_range == "tomorrow":
        tomorrow = (reference_date + timedelta(days=1)).strftime("%Y-%m-%d")
        return (tomorrow, tomorrow)

    if date_range == "this week":
        start_of_week = reference_date - timedelta(days=reference_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return (
            start_of_week.strftime("%Y-%m-%d"),
            end_of_week.strftime("%Y-%m-%d")
        )

    if date_range == "next week":
        start_of_next_week = reference_date - timedelta(days=reference_date.weekday()) + timedelta(days=7)
        end_of_next_week = start_of_next_week + timedelta(days=6)
        return (
            start_of_next_week.strftime("%Y-%m-%d"),
            end_of_next_week.strftime("%Y-%m-%d")
        )

    if date_range == "this month":
        first_of_month = reference_date.replace(day=1)
        if reference_date.month == 12:
            last_of_month = first_of_month.replace(year=first_of_month.year + 1, month=1) - timedelta(days=1)
        else:
            last_of_month = first_of_month.replace(month=first_of_month.month + 1) - timedelta(days=1)
        return (
            first_of_month.strftime("%Y-%m-%d"),
            last_of_month.strftime("%Y-%m-%d")
        )

    if date_range == "next month":
        if reference_date.month == 12:
            first_of_next_month = reference_date.replace(year=reference_date.year + 1, month=1, day=1)
            last_of_next_month = first_of_next_month.replace(month=2) - timedelta(days=1)
        else:
            first_of_next_month = reference_date.replace(month=reference_date.month + 1, day=1)
            if reference_date.month == 11:
                last_of_next_month = first_of_next_month.replace(month=1, year=first_of_next_month.year + 1) - timedelta(days=1)
            else:
                last_of_next_month = first_of_next_month.replace(month=reference_date.month + 2) - timedelta(days=1)
        return (
            first_of_next_month.strftime("%Y-%m-%d"),
            last_of_next_month.strftime("%Y-%m-%d")
        )

    # Handle simple date string
    try:
        parsed_date = _parse_date_string(date_range, reference_date)
        return (
            parsed_date.strftime("%Y-%m-%d"),
            parsed_date.strftime("%Y-%m-%d")
        )
    except ValueError as e:
        raise ValueError(
            f"Invalid date range format: '{date_range}'. "
            f"Expected formats: 'today', 'today to +N', 'YYYY-MM-DD', or 'YYYY-MM-DD to YYYY-MM-DD'"
        ) from e


def _parse_date_string(date_str: str, reference_date: datetime) -> datetime:
    """Parse a date string into a datetime object.

    Supports:
    - "today" or "now" → reference_date
    - "+N" or "-N" → N days from reference_date
    - "YYYY-MM-DD" → explicit date

    Args:
        date_str: Date string to parse
        reference_date: Reference date for relative calculations

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If date format is invalid
    """
    date_str = date_str.strip().lower()

    if date_str in ("today", "now"):
        return reference_date

    if date_str in ("tomorrow", "+1"):
        return reference_date + timedelta(days=1)

    if date_str == "yesterday" or date_str == "-1":
        return reference_date - timedelta(days=1)

    # Handle relative offsets: +N or -N
    if date_str.startswith(("+", "-")):
        try:
            offset_days = int(date_str)
            return reference_date + timedelta(days=offset_days)
        except ValueError as e:
            raise ValueError(f"Invalid relative date offset: {date_str}") from e

    # Handle explicit YYYY-MM-DD format
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD") from e


def is_valid_date_format(date_str: str) -> bool:
    """Check if a string is a valid YYYY-MM-DD date format.

    Args:
        date_str: String to check

    Returns:
        True if valid YYYY-MM-DD format, False otherwise
    """
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except (ValueError, AttributeError):
        return False


def format_date_range_for_display(start_date: str, end_date: str) -> str:
    """Format a date range for human-readable display.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Human-readable date range string
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if start == end:
            return start.strftime("%B %d, %Y")

        if start.year == end.year:
            if start.month == end.month:
                return f"{start.strftime('%B %d')} - {end.strftime('%d, %Y')}"
            return f"{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"

        return f"{start.strftime('%B %d, %Y')} - {end.strftime('%B %d, %Y')}"
    except ValueError:
        return f"{start_date} to {end_date}"


# Additional helper functions
def get_business_days_between(start_date: str, end_date: str) -> int:
    """Count business days (Monday-Friday) between two dates.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Number of business days (inclusive)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    business_days = 0
    current = start

    while current <= end:
        if current.weekday() < 5:  # Monday is 0, Friday is 4
            business_days += 1
        current += timedelta(days=1)

    return business_days


def add_business_days(start_date: str, num_days: int) -> str:
    """Add business days to a date, skipping weekends.

    Args:
        start_date: Start date in YYYY-MM-DD format
        num_days: Number of business days to add

    Returns:
        Result date in YYYY-MM-DD format
    """
    current = datetime.strptime(start_date, "%Y-%m-%d")
    days_added = 0

    while days_added < num_days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday is 0, Friday is 4
            days_added += 1

    return current.strftime("%Y-%m-%d")
