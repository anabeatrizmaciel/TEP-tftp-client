from pathlib import Path

from tftp_client.files import FileManager


def test_read_and_write_bytes(tmp_path: Path):
    fm = FileManager()
    file_path = tmp_path / "sample.txt"
    fm.write_bytes(file_path, b"hello")
    assert fm.read_bytes(file_path) == b"hello"


def test_iter_chunks_empty_file(tmp_path: Path):
    fm = FileManager()
    file_path = tmp_path / "empty.txt"
    file_path.write_bytes(b"")
    assert list(fm.iter_chunks(file_path)) == [b""]
