import tempfile
from pathlib import Path
from organizer import organize_directory, detect_category_by_extension, CATEGORY_MAP

def test_detect_known_extension():
    assert detect_category_by_extension("jpg") == "Images"
    assert detect_category_by_extension(".mp4") == "Videos" or detect_category_by_extension("mp4") == "Videos"

def test_organize_directory_dry_run(tmp_path):
    # create files
    a = tmp_path / "photo.jpg"; a.write_text("x")
    b = tmp_path / "doc.pdf"; b.write_text("x")
    c = tmp_path / "archive.zip"; c.write_text("x")

    report = organize_directory(tmp_path, dry_run=True)
    moved_names = {m["from"] for m in report["moved"]}
    assert "photo.jpg" in moved_names
    assert "doc.pdf" in moved_names
    assert "archive.zip" in moved_names

def test_organize_directory_move(tmp_path):
    a = tmp_path / "song.mp3"; a.write_text("x")
    report = organize_directory(tmp_path, dry_run=False)
    # ensure file moved to category folder
    assert any("song.mp3" in m["to"] for m in report["moved"])
    # target folder exists
    assert any((tmp_path / "Audio").exists() for _ in [0])