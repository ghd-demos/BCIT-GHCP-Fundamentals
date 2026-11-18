import logging
from pathlib import Path

from rename_globex_symbols import EXIT_FAILURE, EXIT_SUCCESS, run

LOGGER_NAME = "rename_globex_symbols"




def test_renames_matching_file_and_symbol(tmp_path: Path) -> None:
	source = tmp_path / "globex_client.py"
	source.write_text("def globex_request():\n    return globex_status\n", encoding="utf-8")

	result = run(tmp_path, check=False)

	assert result == EXIT_SUCCESS
	destination = tmp_path / "chroma_client.py"
	assert not source.exists()
	assert destination.read_text(encoding="utf-8") == (
		"def chroma_request():\n    return chroma_status\n"
	)


def test_skips_binary_files_and_reports_them(tmp_path: Path, caplog) -> None:
	caplog.set_level(logging.INFO, logger=LOGGER_NAME)
	binary_file = tmp_path / "globex_asset.bin"
	original = b"\xff\xfe\x00globex_value"
	binary_file.write_bytes(original)

	result = run(tmp_path, check=False)



	assert result == EXIT_SUCCESS
	assert binary_file.exists()
	assert binary_file.read_bytes() == original
	assert "Binary files skipped: 1" in caplog.text


def test_check_reports_changes_without_modifying_files(tmp_path: Path, caplog) -> None:
	caplog.set_level(logging.INFO, logger=LOGGER_NAME)
	source = tmp_path / "globex_service.py"
	original = "globex_handler = True\n"
	source.write_text(original, encoding="utf-8")

	result = run(tmp_path, check=True)


	output = caplog.text

	assert result == EXIT_FAILURE
	assert source.read_text(encoding="utf-8") == original
	assert source.exists()
	assert not (tmp_path / "chroma_service.py").exists()
	assert "Would rename:" in output
	assert "Symbol replacements: 1" in output
	assert "Check mode: yes" in output
