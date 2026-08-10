# repository.py.tpl


# AUTO GENERATED

from src.application.ports.patient_device_assignment_repository_port import (
    PatientDeviceAssignmentRepositoryPort,
)

from src.domain.entities.patient_device_assignment_entities import (
    PatientDeviceAssignment,
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

from src.infrastructure.persistence.mappers.patient_device_assignment.patient_device_assignment_row_mapper import (
    PatientDeviceAssignmentRowMapper,
)


from src.infrastructure.persistence.schemas.patient_device_assignment.patient_device_assignment_columns import (
    PatientDeviceAssignmentColumns,
)


class GoogleSheetsPatientDeviceAssignmentRepository(
    GoogleSheetsRepository,
    PatientDeviceAssignmentRepositoryPort,
):

    TABLE_NAME = "patient_device_assignment"
    ID_COLUMN = PatientDeviceAssignmentColumns.PATIENT_ID


    def __init__(
        self,
        *,
        query_service: GoogleSheetsQueryService,
        catalog: GoogleSheetCatalog,
        mapper: PatientDeviceAssignmentRowMapper,
    ) -> None:

        super().__init__(
            query_service=query_service,
            catalog=catalog,
        )

        self._mapper = mapper

    def list_patient_device_assignments(self) -> tuple[PatientDeviceAssignment, ...]:

        return tuple(
            self._mapper.to_domain(row)
            for row in self._read_rows()
        )


    def get_by_id(
            self,
            patient_id: str,
    ) -> PatientDeviceAssignment:
        raw_row = self._find_single_row(
            rows=self._read_rows(),
            column_name=self.ID_COLUMN,
            value=patient_id,
        )

        return self._mapper.to_domain(raw_row)
