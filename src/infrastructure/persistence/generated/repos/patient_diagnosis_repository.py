# repository.py.tpl


# AUTO GENERATED

from src.application.ports.patient_diagnosis_repository_port import (
    PatientDiagnosisRepositoryPort,
)

from src.domain.entities.patient_diagnosis_entities import (
    PatientDiagnosis,
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

from src.infrastructure.persistence.mappers.patient_diagnosis.patient_diagnosis_row_mapper import (
    PatientDiagnosisRowMapper,
)


from src.infrastructure.persistence.schemas.patient_diagnosis.patient_diagnosis_columns import (
    PatientDiagnosisColumns,
)


class GoogleSheetsPatientDiagnosisRepository(
    GoogleSheetsRepository,
    PatientDiagnosisRepositoryPort,
):

    TABLE_NAME = "patient_diagnosis"
    ID_COLUMN = PatientDiagnosisColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: PatientDiagnosisRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_patient_diagnosises(self) -> tuple[PatientDiagnosis, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> PatientDiagnosis:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
