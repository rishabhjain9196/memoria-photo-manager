import json
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
os.environ["MEMORIA_PROFILE"] = "Memoria-Tests"   # keep UI tests out of the user's real settings
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import make_test_library  # noqa: E402
from memoria.engine import scanner  # noqa: E402
from memoria.engine.db import Library  # noqa: E402


@pytest.fixture(scope="session")
def pristine_library(tmp_path_factory) -> Path:
    """A small generated library, built once per test session. Never mutate it directly."""
    dest = tmp_path_factory.mktemp("pristine") / "library"
    make_test_library.build(dest, small=True, videos=True)
    return dest


@pytest.fixture(scope="session")
def indexed_template(pristine_library, tmp_path_factory) -> Path:
    """The pristine library copied and fully indexed once (speeds up tests that copy it)."""
    dest = tmp_path_factory.mktemp("indexed") / "library"
    shutil.copytree(pristine_library, dest, copy_function=shutil.copy2)
    lib = Library(dest)
    scanner.index(lib)
    lib.close()
    return dest


@pytest.fixture
def library(indexed_template, tmp_path) -> Library:
    """A fresh, indexed, mutable copy of the test library for one test."""
    dest = tmp_path / "library"
    shutil.copytree(indexed_template, dest, copy_function=shutil.copy2)
    lib = Library(dest)
    yield lib
    lib.close()


@pytest.fixture
def expected(pristine_library) -> dict:
    return json.loads((pristine_library / "expected.json").read_text())
