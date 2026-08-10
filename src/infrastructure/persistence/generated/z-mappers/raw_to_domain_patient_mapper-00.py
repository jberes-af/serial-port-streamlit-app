# /src/infrastructure/persistence/google/google_sheets/repos/raw_to_domain_patient_mapper.py

from src.domain.entities.patient_entities import (
    PatientAdministration,
)
from src.infrastructure.persistence.common.types import RawRow

from src.infrastructure.persistence.common.utils_parsing import (
    parse_optional_text,
)

from src.infrastructure.persistence.schemas.patient_schemas import PatientAdminColumns


class PatientAdminRowMapper:
    @staticmethod
    def to_domain(row: RawRow) -> PatientAdministration:
        schema = PatientAdminColumns
        return PatientAdministration(
            patient_id=parse_optional_text(
                row.get(schema.PATIENT_ID),
            ),
            first_name=parse_optional_text(
                row.get(schema.FIRST_NAME),
            ),
            middle_name=parse_optional_text(
                row.get(schema.MIDDLE_NAME),
            ),
            last_name=parse_optional_text(
                row.get(schema.LAST_NAME),
            ),
            date_of_birth=parse_optional_text(
                row.get(schema.DATE_OF_BIRTH),
            ),
            telephone=parse_optional_text(
                row.get(schema.TELEPHONE),
            ),
            email=parse_optional_text(
                row.get(schema.EMAIL),
            ),
            address_line_1=parse_optional_text(
                row.get(schema.ADDRESS_LINE_1),
            ),
            address_line_2=parse_optional_text(
                row.get(schema.ADDRESS_LINE_2),
            ),
            city=parse_optional_text(
                row.get(schema.CITY),
            ),
            state=parse_optional_text(
                row.get(schema.STATE),
            ),
            postal_code=parse_optional_text(
                row.get(schema.POSTAL_CODE),
            ),
            primary_payer_id=parse_optional_text(
                row.get(schema.PRIMARY_PAYER_ID),
            ),
            primary_diagnosis_id=parse_optional_text(
                row.get(schema.PRIMARY_DIAGNOSIS_ID),
            ),
            additional_diagnosis_ids=parse_optional_text(
                row.get(schema.ADDITIONAL_DIAGNOSIS_IDS),
            ),
            treating_provider_id=parse_optional_text(
                row.get(schema.TREATING_PROVIDER_ID),
            ),
            ordering_provider_id=parse_optional_text(
                row.get(schema.ORDERING_PROVIDER_ID),
            ),
            supervising_provider_id=parse_optional_text(
                row.get(schema.SUPERVISING_PROVIDER_ID),
            ),
)