from datetime import datetime
from zoneinfo import ZoneInfo

from schemas import AirShipmentExtraction


def build_air_draft(
    shipment: AirShipmentExtraction,
    validation: dict,
    bill_to: str,
) -> dict:
    form_values = {}
    field_statuses = {}

    # Select only single candidates whose evidence matched
    # and which have no reported uncertainty.
    for field_name, field in shipment:
        status = validation[field_name]["status"]

        if status == "evidence_matched":
            form_values[field_name] = field.candidates[0].value
        else:
            form_values[field_name] = ""

        field_statuses[field_name] = status

    # DATE is today's date in the office's timezone.
    form_values["date"] = datetime.now(
        ZoneInfo("America/Toronto")
    ).strftime("%d-%m-%Y")
    field_statuses["date"] = "system_value"

    # Fixed billing information supplied by our application.
    form_values["bill_to"] = bill_to
    field_statuses["bill_to"] = "configured_value"

    # Both references use the same shipment identifier.
    form_values["invoicing_reference"] = form_values["file_number"]
    field_statuses["invoicing_reference"] = (
        field_statuses["file_number"]
    )

    # Only construct a route when both endpoints were selected.
    origin = form_values["origin_airport"]
    destination = form_values["destination_airport"]

    if origin and destination:
        form_values["route"] = f"{origin} -- {destination}"
        field_statuses["route"] = "derived"
    else:
        form_values["route"] = ""
        field_statuses["route"] = "needs_review"

    # Use the package default only when nothing was extracted.
    # Do not replace a conflicting or invalid package count with 1.
    if field_statuses["package_count"] == "missing":
        form_values["package_count"] = "1"
        field_statuses["package_count"] = "defaulted"

    # Arrival date is not applicable to exports.
    direction = form_values["shipment_direction"].strip().lower()

    if direction == "export":
        form_values["arrival_date"] = ""
        field_statuses["arrival_date"] = "not_applicable"
    elif direction != "import":
        # Staff must resolve the direction before using arrival date.
        form_values["arrival_date"] = ""
        field_statuses["arrival_date"] = "needs_review"

    # Apply the single-weight fallback only when exactly one
    # weight field has candidates, and its value passed selection.
    weight_fields = [
        "gross_weight",
        "chargeable_weight",
        "unspecified_weight",
    ]

    #populated_weight_fields includes that key’s name only when its status isn’t "missing"
    #validation always has "unspecified_weight" but it might has a missing status or not.
    populated_weight_fields = [
        name
        for name in weight_fields
        if validation[name]["status"] != "missing"
    ]
    #If exactly one weight field has candidates, retrieve its selected value and copy it to the other
    # weight fields
    if len(populated_weight_fields) == 1:
        source_field = populated_weight_fields[0]
        weight = form_values[source_field]

        if weight:
            for target in ["gross_weight", "chargeable_weight"]:
                if not form_values[target]:
                    form_values[target] = weight
                    field_statuses[target] = (
                        f"copied_from_{source_field}"
                    )

    # If several weight fields have candidates and one is 
    # unspecified_weight, mark both gross and chargeable as needs_review 
    # (since the unspecified_weight might actually be the weight that we 
    # need to use for "chargable or gross weight")
    if (
        len(populated_weight_fields) > 1
        and "unspecified_weight" in populated_weight_fields
    ):
        for name in ["gross_weight", "chargeable_weight"]:
            field_statuses[name] = "needs_review"

    # The original unspecified_weight and its evidence remain in shipment 
    # and validation for review. We’re only removing it from the form-facing draft.
    form_values.pop("unspecified_weight")
    field_statuses.pop("unspecified_weight")

    return {
        "template_id": "air_do",
        "form_values": form_values,
        "field_statuses": field_statuses,
    }