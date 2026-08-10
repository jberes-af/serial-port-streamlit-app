# repository.py.tpl


# AUTO GENERATED

from src.application.ports.patient_payer_repository_port import (
    PatientPayerRepositoryPort,
)

from src.domain.entities.patient_payer_entities import (
    PatientPayer,
)

from src.infrastructure.persistence.google_sheets.base_repository import (
    GoogleSheetsRepository,
)

from src.infrastructure.persistence.google_sheets.google_sheet_catalog import (
    GoogleSheetCatalog,
)

from src.infrastructure.persistence.google_sheets.sheets_query_service import (
    GoogleSheetsQueryService,
)

from src.infrastructure.persistence.mappers.patient_payer.patient_payer_row_mapper import (
    PatientPayerRowMapper,
)


from src.infrastructure.persistence.schemas.patient_payer.patient_payer_columns import (
    PatientPayerColumns,
)


class GoogleSheetsPatientPayerRepository(
    GoogleSheetsRepository,
    PatientPayerRepositoryPort,
):

    TABLE_NAME = "patient_payer"
    ID_COLUMN = PatientPayerColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: PatientPayerRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_patient_payers(self) -> tuple[PatientPayer, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> PatientPayer:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
