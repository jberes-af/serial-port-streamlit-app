# AUTO GENERATED

from src.infrastructure.persistence.common.types import RawRow

from src.infrastructure.persistence.schemas.patient.patient_columns import PatientColumns

from src.domain.entities.patient_entities import Patient

from src.infrastructure.persistence.common.utils_parsing import *

class PatientRowMapper:

    @staticmethod
    def to_domain(row: RawRow) -> Patient:

        schema = PatientColumns

        return Patient(
            patient_id=parse_required_text(
                row.get(schema.PATIENT_ID),
                field_name=schema.PATIENT_ID,
            ),
            first_name=parse_required_text(
                row.get(schema.FIRST_NAME),
                field_name=schema.FIRST_NAME,
            ),
            middle_name=parse_optional_text(
                row.get(schema.MIDDLE_NAME),
                field_name=schema.MIDDLE_NAME,
            ),
            last_name=parse_required_text(
                row.get(schema.LAST_NAME),
                field_name=schema.LAST_NAME,
            ),
            date_of_birth=parse_required_date(
                row.get(schema.DATE_OF_BIRTH),
                field_name=schema.DATE_OF_BIRTH,
            ),
            telephone=parse_optional_text(
                row.get(schema.TELEPHONE),
                field_name=schema.TELEPHONE,
            ),
            email=parse_optional_text(
                row.get(schema.EMAIL),
                field_name=schema.EMAIL,
            ),
            address_line_1=parse_optional_text(
                row.get(schema.ADDRESS_LINE_1),
                field_name=schema.ADDRESS_LINE_1,
            ),
            address_line_2=parse_optional_text(
                row.get(schema.ADDRESS_LINE_2),
                field_name=schema.ADDRESS_LINE_2,
            ),
            city=parse_optional_text(
                row.get(schema.CITY),
                field_name=schema.CITY,
            ),
            state=parse_optional_text(
                row.get(schema.STATE),
                field_name=schema.STATE,
            ),
            postal_code=parse_optional_text(
                row.get(schema.POSTAL_CODE),
                field_name=schema.POSTAL_CODE,
            ),
        )