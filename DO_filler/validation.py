from schemas import AirShipmentExtraction


def normalize_whitespace(text: str) -> str:
    """Treat repeated spaces, tabs, and line breaks as single spaces."""
    return " ".join(text.split())


def validate_evidence(
    shipment: AirShipmentExtraction,
    sources: dict,
) -> dict:
    report = {}

    for field_name, field in shipment:
        candidate_reports = []

        for index, candidate in enumerate(field.candidates):
            issues = []

            if not candidate.value.strip():
                issues.append("Candidate value is empty.")

            for evidence in candidate.evidence:
                source = sources.get(evidence.source_id)

                if source is None:
                    issues.append(
                        f"Unknown source: {evidence.source_id}"
                    )
                    continue

                quote = normalize_whitespace(evidence.quote)
                source_text = normalize_whitespace(source["text"])

                if not quote:
                    issues.append("Evidence quote is empty.")
                elif quote not in source_text:
                    issues.append(
                        f"Quote not found in {evidence.source_id}: "
                        f"{evidence.quote}"
                    )

            candidate_reports.append({
                "candidate_index": index,
                "value": candidate.value,
                "evidence_passed": not issues,
                "issues": issues,
                "uncertainty": candidate.uncertainty,
            })

        if not field.candidates:
            status = "missing"
        #Does at least one candidate have evidence_passed=False?”
        elif any(
            not result["evidence_passed"]
            for result in candidate_reports
        ):
            status = "evidence_issue"
        elif len(field.candidates) > 1:
            status = "multiple_candidates"
        elif field.candidates[0].uncertainty:
            status = "uncertain"
        else:
            status = "evidence_matched"

        report[field_name] = {
            "status": status,
            "candidates": candidate_reports,
        }

    return report

# Field status rules (checked top to bottom; the first match wins)
#
# +------------------------------------------+----------------------+---------------------------------------------------------+
# | Condition                                | Field status         | Meaning                                                 |
# +------------------------------------------+----------------------+---------------------------------------------------------+
# | No candidates                            | "missing"            | No value was extracted.                                 |
# | Any candidate failed an evidence check   | "evidence_issue"     | At least one source or quote is invalid.                |
# | More than one candidate                  | "multiple_candidates"| There are alternative values to review.                 |
# | Single candidate has an uncertainty note | "uncertain"          | The AI identified an ambiguity.                         |
# | Otherwise                                | "evidence_matched"   | One candidate, matching evidence, no reported           |
# |                                          |                      | uncertainty.                                            |
# +------------------------------------------+----------------------+---------------------------------------------------------+