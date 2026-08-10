# /src/infrastructure/persistence/google/google_sheets/utils_parsing.py

from datetime import date, datetime, time
from typing import Any


def parse_text(
        value: Any,
) -> str:
    if value is None:
        return ""

    return str(value).strip()


def parse_required_text(
        value: Any,
        field_name: str,
) -> str:
    text = parse_text(value)

    if not text:
        raise ValueError(
            f"Missing required field: {field_name}"
        )

    return text


def parse_optional_text(
        value: Any,
        field_name: str,
) -> str | None:
    del field_name

    text = parse_text(value)

    return text or None


def parse_required_int(
        value: Any,
        field_name: str,
) -> int:
    number = parse_optional_int(
        value,
        field_name,
    )

    if number is None:
        raise ValueError(
            f"Missing required field: {field_name}"
        )

    return number


def parse_optional_int(
        value: Any,
        field_name: str,
) -> int | None:
    if value is None:
        return None

    text = parse_text(value)

    if not text:
        return None

    normalized = text.replace(",", "")

    try:
        return int(normalized)

    except ValueError as ex:
        raise ValueError(
            f"Invalid integer value for "
            f"{field_name}: {text!r}"
        ) from ex


def parse_required_date(
        value: Any,
        field_name: str,
) -> date:
    parsed = parse_optional_date(
        value,
        field_name,
    )

    if parsed is None:
        raise ValueError(
            f"Missing required field: {field_name}"
        )

    return parsed


def parse_optional_date(
        value: Any,
        field_name: str,
) -> date | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    text = parse_text(value)

    if not text:
        return None

    accepted_formats = (
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
    )

    for date_format in accepted_formats:
        try:
            return datetime.strptime(
                text,
                date_format,
            ).date()

        except ValueError:
            continue

    raise ValueError(
        f"Invalid date value for {field_name}: "
        f"{text!r}"
    )


def parse_required_time(
        value: Any,
        field_name: str,
) -> time:
    parsed = parse_optional_time(
        value,
        field_name,
    )

    if parsed is None:
        raise ValueError(
            f"Missing required field: {field_name}"
        )

    return parsed


def parse_optional_time(
        value: Any,
        field_name: str,
) -> time | None:
    if value is None:
        return None

    if isinstance(value, time):
        return value

    text = parse_text(value)

    if not text:
        return None

    accepted_formats = (
        "%H:%M:%S",
        "%H:%M",
        "%I:%M %p",
        "%I:%M:%S %p",
    )

    for time_format in accepted_formats:
        try:
            return datetime.strptime(
                text,
                time_format,
            ).time()

        except ValueError:
            continue

    raise ValueError(
        f"Invalid time value for "
        f"{field_name}: {text!r}"
    )


def parse_required_bool(
        value: Any,
        field_name: str,
) -> bool:
    parsed = parse_optional_bool(
        value,
        field_name,
    )

    if parsed is None:
        raise ValueError(
            f"Missing required field: {field_name}"
        )

    return parsed


def parse_optional_bool(
        value: Any,
        field_name: str,
) -> bool | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    text = parse_text(value)

    if not text:
        return None

    normalized = text.lower()

    if normalized in (
            "true",
            "t",
            "yes",
            "y",
            "1",
    ):
        return True

    if normalized in (
            "false",
            "f",
            "no",
            "n",
            "0",
    ):
        return False

    raise ValueError(
        f"Invalid boolean value for "
        f"{field_name}: {text!r}"
    )


def parse_optional_datetime(
        value: Any,
        field_name: str,
) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    text = parse_text(value)

    if not text:
        return None

    accepted_formats = (
        # ISO-8601
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",

        # US formats
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y %I:%M:%S %p",

        "%m/%d/%y %H:%M:%S",
        "%m/%d/%y %H:%M",
        "%m/%d/%y %I:%M %p",
        "%m/%d/%y %I:%M:%S %p",
    )

    for datetime_format in accepted_formats:
        try:
            return datetime.strptime(
                text,
                datetime_format,
            )

        except ValueError:
            continue

    raise ValueError(
        f"Invalid datetime value for "
        f"{field_name}: {text!r}"
    )


def parse_required_datetime(
        value: Any,
        field_name: str,
) -> datetime:
    parsed = parse_optional_datetime(
        value,
        field_name,
    )

    if parsed is None:
        raise ValueError(
            f"Missing required field: {field_name}"
        )

    return parsed
