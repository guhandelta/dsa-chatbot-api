# Framework reference source snapshots

These authored curriculum sources make `tools/repair_reference_sections.py`
and its regression tests runnable from a clean API checkout. When the original
files exist under the workspace's `output/pdf/` directory, the repair tool still
uses those operator sources. Otherwise it reads these snapshots.

When intentionally updating either curriculum, update its snapshot along with
the derived reference records and run `tests/test_reference_maintenance.py`.
