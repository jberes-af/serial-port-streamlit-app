# repository.py.tpl


# AUTO GENERATED

from src.application.ports.patient_repository_port import (
    PatientRepositoryPort,
)

from src.domain.entities.patient_entities import (
    Patient,
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

from src.infrastructure.persistence.mappers.patient.patient_row_mapper import (
    PatientRowMapper,
)


from src.infrastructure.persistence.schemas.patient.patient_columns import (
    PatientColumns,
)


class GoogleSheetsPatientRepository(
    GoogleSheetsRepository,
    PatientRepositoryPort,
):

    TABLE_NAME = "patient"
    ID_COLUMN = PatientColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: PatientRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_patients(self) -> tuple[Patient, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> Patient:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
