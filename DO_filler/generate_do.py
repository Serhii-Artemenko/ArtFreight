"""Render an Air D.O. HTML preview. It's for testing does not call 
the LLM or approve a draft."""
import argparse
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

BASE_DIR = Path(__file__).resolve().parent
PRINT_FIELDS = (
    "date", "file_number", "trucker", "pickup_location", "delivery_location",
    "pickup_date", "delivery_date", "origin_airport", "destination_airport",
    "carrier", "awb_number", "arrival_date", "mark", "goods_description",
    "package_count", "gross_weight", "chargeable_weight", "bill_to",
    "invoicing_reference", "route",
)


def render_air_do(draft: dict, output_path: Path | None = None) -> Path:
    """Render existing values without guessing, changing or approving them.

    Source text is escaped as HTML. Newlines are preserved by CSS.
    Extra draft keys are ignored; absent print fields are errors.
    """
    if draft.get("template_id") != "air_do":
        raise ValueError("Expected template_id='air_do'.")
    values = draft.get("form_values")
    if not isinstance(values, dict):
        raise ValueError("draft must contain a form_values dictionary.")
    missing = [key for key in PRINT_FIELDS if key not in values]
    if missing:
        raise ValueError(f"Missing form keys (use empty strings for blanks): {missing}")
    for key in PRINT_FIELDS:
        if not isinstance(values[key], str):
            raise TypeError(f"form_values[{key!r}] must be a string.")

    environment = Environment(
        loader=FileSystemLoader(BASE_DIR / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
    )
    statuses = draft.get("field_statuses", {})
    review_items = [
        key.replace("_", " ")
        for key, status in statuses.items()
        if status in {"needs_review", "evidence_issue", "multiple_candidates", "uncertain"}
    ]
    template = environment.get_template("air_do.html")
    html = template.render(
        **{key: values[key] for key in PRINT_FIELDS},
        review_items=review_items, #--> we specify that the items to be reviewed is the review_items list the html/css will handle that
    )
    path = Path(output_path) if output_path else BASE_DIR / "output" / "air_do_preview.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path.resolve()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", nargs="?", type=Path,
                        default=BASE_DIR / "examples" / "las_vegas_draft.json")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    draft_data = json.loads(args.draft.read_text(encoding="utf-8"))
    result = render_air_do(draft_data, args.output)
    print(f"HTML preview saved to: {result}")
    print("Open in a browser. Print: Letter, 100%, browser headers/footers off.")
