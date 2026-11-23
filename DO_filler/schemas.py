#Here we will define the LLM response
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    # Reject unexpected fields instead of silently ignoring them.
    model_config = ConfigDict(extra="forbid")


class Evidence(StrictModel):
    # Must match a key in our sources dictionary.
    source_id: str

    # Text copied from that source to support the proposed value.
    quote: str


class Candidate(StrictModel):
    # Keep extracted values as text for now, including units.
    # Example: "302 kg"
    value: str

    # Every candidate must have at least one supporting quote.
    evidence: list[Evidence] = Field(min_length=1)

    # Explanation of an ambiguity, or null if none was identified.
    uncertainty: str | None


class ExtractedField(StrictModel):
    # No information: []
    # One supported value: one candidate
    # Conflicting information: multiple candidates
    candidates: list[Candidate]


class AirShipmentExtraction(StrictModel):
    shipment_direction: ExtractedField  # import or export
    file_number: ExtractedField
    trucker: ExtractedField

    pickup_location: ExtractedField
    delivery_location: ExtractedField

    origin_airport: ExtractedField
    destination_airport: ExtractedField
    carrier: ExtractedField
    awb_number: ExtractedField

    arrival_date: ExtractedField
    pickup_date: ExtractedField
    delivery_date: ExtractedField

    mark: ExtractedField
    goods_description: ExtractedField
    package_count: ExtractedField

    gross_weight: ExtractedField
    chargeable_weight: ExtractedField

    # For an email saying only "210 kg", without specifying weight type.
    unspecified_weight: ExtractedField
