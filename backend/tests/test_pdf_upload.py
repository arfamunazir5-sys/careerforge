"""Phase 7 tests: PDF resume text extraction (in memory, nothing stored)."""
import app.analysis.pdf_text as pdf_text
from app.analysis.pdf_text import extract_text_from_pdf


def make_pdf(lines):
    """Builds a tiny valid one-page PDF containing the given text lines."""
    content = "BT /F1 12 Tf 72 720 Td " + " ".join(f"({line}) Tj 0 -16 Td" for line in lines) + " ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        "/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n{body}\nendobj\n".encode()
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return out


def upload(client, data, name="resume.pdf", content_type="application/pdf"):
    return client.post("/extract-resume-text", files={"file": (name, data, content_type)})


def state(c):
    return c.get("/state").json()


def test_text_is_extracted_from_a_pdf(client):
    r = upload(client, make_pdf(["Education", "Experience", "Built APIs with Python and SQL"]))
    assert r.status_code == 200
    body = r.json()
    assert "Built APIs with Python and SQL" in body["text"] and "Education" in body["text"]
    assert body["pages"] == 1 and body["truncated"] is False and body["chars"] == len(body["text"])


def test_extracted_text_feeds_the_resume_analysis(client):
    text = upload(client, make_pdf(["Education Experience Projects Skills", "Python SQL Git Docker"])).json()["text"]
    result = client.post("/analyze-resume", json={"resume_text": text, "target_role": "swe_backend"}).json()
    assert "python" not in result["missing_skills"] and "docker" not in result["missing_skills"]
    assert "flask" in result["missing_skills"]


def test_a_pdf_without_text_is_rejected_with_a_helpful_message(client):
    r = upload(client, make_pdf([]))
    assert r.status_code == 422 and "scanned" in r.json()["detail"]


def test_non_pdf_files_are_rejected(client):
    r = upload(client, b"just some text", name="resume.pdf")
    assert r.status_code == 422 and "not a PDF" in r.json()["detail"]
    assert upload(client, b"", name="resume.pdf").status_code == 422


def test_damaged_pdf_is_rejected(client):
    r = upload(client, b"%PDF-1.4\n this is not really a pdf \n%%EOF")
    assert r.status_code == 422 and "Could not read" in r.json()["detail"]


def test_oversized_pdf_is_rejected(client):
    r = upload(client, b"%PDF-" + b"0" * (pdf_text.MAX_BYTES + 10))
    assert r.status_code == 413 and "2 MB" in r.json()["detail"]


def test_missing_file_field_is_a_validation_error(client):
    assert client.post("/extract-resume-text").status_code == 422


def test_long_text_is_truncated_and_flagged(monkeypatch):
    monkeypatch.setattr(pdf_text, "MAX_CHARS", 12)
    result = extract_text_from_pdf(make_pdf(["A fairly long line of resume text"]))
    assert result["truncated"] is True and len(result["text"]) <= 12


def test_uploading_a_resume_changes_no_stored_state(client):
    before = state(client)
    upload(client, make_pdf(["Education", "Python"]))
    assert state(client) == before