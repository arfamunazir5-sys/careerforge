from app.export.calendar_export import build_ics_content


def test_ics_content_has_valid_structure():
    tasks = [
        {"id": "t1", "agent": "skill_building", "title": "Complete a tutorial on flask", "hours": 2, "status": "pending"},
        {"id": "t2", "agent": "networking", "title": "Send 3 connection requests", "hours": 1, "status": "pending"},
    ]

    ics = build_ics_content(tasks)

    assert ics.startswith("BEGIN:VCALENDAR")
    assert ics.strip().endswith("END:VCALENDAR")
    assert ics.count("BEGIN:VEVENT") == 2
    assert ics.count("END:VEVENT") == 2
    assert "Complete a tutorial on flask" in ics
    assert "Send 3 connection requests" in ics
    print(ics)


def test_ics_escapes_special_characters():
    tasks = [
        {"id": "t1", "agent": "skill_building", "title": "Review notes, then practice; repeat", "hours": 1, "status": "pending"},
    ]
    ics = build_ics_content(tasks)
    assert "notes\\, then practice\\; repeat" in ics
    