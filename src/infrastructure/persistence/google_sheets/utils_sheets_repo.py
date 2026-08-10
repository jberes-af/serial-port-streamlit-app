# /src/infrastructure/persistence/google_sheets/utils_sheets_repo.py


def _column_number_to_letter(
        column_number: int,
) -> str:
    if column_number < 1:
        raise ValueError(
            "column_number must be at least 1"
        )

    letters: list[str] = []

    while column_number:
        column_number, remainder = divmod(
            column_number - 1,
            26,
        )
        letters.append(chr(65 + remainder))

    return "".join(reversed(letters))


def _worksheet_name_from_range(
        range_a1: str,
) -> str:
    worksheet_part, separator, _ = range_a1.partition("!")

    if not separator:
        raise ValueError(
            f"Invalid A1 range: {range_a1!r}"
        )

    return worksheet_part.strip("'")
