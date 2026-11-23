from pathlib import Path
from pypdf import PdfReader


def extract_sources(email_text: str, pdf_paths: list[Path]) -> dict:
    """ This will return a dict of this format:

    """

    #So basically we start with a dict with one entry the email 
    #(since we work with one email at a time we just manually add the one email)
    if not email_text.strip():
        raise ValueError("The pasted email is emtpy")
    sources = {
        "email_1":{
            "filename": None,
            "page": None,
            "text": email_text.strip(),
        }
    }

    # 1, .//../pd1 etc. --> 1, path_to_pdf
    for pdf_number, path in enumerate(pdf_paths, start = 1):
        reader = PdfReader(path)

        #now check each page in each pdf
        for page_number, page in enumerate(reader.pages, start = 1):
            text = page.extract_text(extraction_mode="layout") or "" #Layout = preserver text positioning where possible
            if not text.strip():
                raise ValueError(f"No readable text on page {page_number} of {path.name}")
            #Now we will extract the source of our info:
            source_id = f"pdf_{pdf_number}_page_{page_number}"
            sources[source_id] = {
                "filename": path.name,
                "page": page_number,
                "text": text.strip(),
            }
            #each DO is its own operation so we build one dictionary per submission (may be creating more then one DO later) and this dict contains the email_1 
            #and the source_id which is just the pdf_number+pdf_page and the value is the path to that pdf 
            #the page number and its contents (text)

    return sources



if __name__ == "__main__":
    email = Path("las_vegas_email.txt").read_text(encoding="utf-8")
    sources = extract_sources(email, [Path("Laser MAWB - Ordered.pdf")])

    print("Source IDs:", list(sources))
    print(sources["pdf_1_page_1"]["text"])






