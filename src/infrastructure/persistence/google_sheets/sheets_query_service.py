# /infrastructure/google/sheets_query_service.py

from dataclasses import dataclass
from typing import Any
from src.infrastructure.persistence.google_sheets.google_retry_utility import retry_google_api_operation


@dataclass(frozen=True)
class GoogleSheetsQueryService:
    sheets_service: Any  # googleapiclient.discovery.Resource

    def read_values(self,
                    *,
                    spreadsheet_id: str,
                    range_a1: str) -> list[dict[str, str]]:
        def op():
            return (
                self.sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_a1)
                .execute()
            )

        result = retry_google_api_operation(op)
        values = result.get("values", [])
        if not values:
            return []

        """
        normalized: list[list[str]] = []
        for row in values:
            normalized.append([("" if cell is None else str(cell)) for cell in row])
        """

        headers: list[str] = values[0]
        data_rows: list[list[str]] = values[1:]

        normalized_rows: list[dict[str, str]] = []
        for row in data_rows:
            row_dict: dict[str, str] = {}
            for index, header in enumerate(headers):
                row_dict[header] = row[index] if index < len(row) else ""
            normalized_rows.append(row_dict)

        return normalized_rows

    def append_values(
            self,
            *,
            spreadsheet_id: str,
            range_a1: str,
            values: list[list[str]],
            value_input_option: str = "RAW",
            insert_data_option: str = "INSERT_ROWS",
    ) -> None:
        """
        Append rows to a sheet range.
        range_a1 should include the tab name, e.g. "contracts!A:K"
        """
        body = {"values": values}

        def op():
            return (
                self.sheets_service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_a1,
                    valueInputOption=value_input_option,
                    insertDataOption=insert_data_option,
                    body=body,
                )
                .execute()
            )

        retry_google_api_operation(op)

    def update_values(
            self,
            *,
            spreadsheet_id: str,
            range_a1: str,
            values: list[list[str]],
            value_input_option: str = "RAW",
    ) -> None:
        body = {
            "values": values,
        }

        def op():
            return (
                self.sheets_service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_a1,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )

        retry_google_api_operation(op)
