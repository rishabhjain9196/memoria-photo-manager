import pytest

from memoria.engine import disk_speed


@pytest.mark.parametrize("info, network, media, workers", [
    ({"seek_penalty": True, "bus_type": "USB"}, False, "hdd", 1),
    ({"seek_penalty": True, "bus_type": "SATA"}, False, "hdd", 2),
    ({"seek_penalty": None, "trim": None, "bus_type": "USB"}, False, "hdd", 1),
    ({"seek_penalty": None, "trim": True, "bus_type": "SAS"}, False, "ssd", None),
    ({"seek_penalty": False, "bus_type": "USB"}, False, "ssd", None),
    ({}, True, "unknown", 2),
])
def test_media_classification(info, network, media, workers, tmp_path, monkeypatch):
    monkeypatch.delenv("MEMORIA_IO_WORKERS", raising=False)
    plan = disk_speed._classify(info, tmp_path, network)
    assert (plan["is_hdd"], plan["is_ssd"]) == (media == "hdd", media == "ssd")
    if workers is not None:
        assert plan["workers"] == workers


def test_unknown_media_with_no_timing_sample_is_not_called_an_ssd(tmp_path, monkeypatch):
    monkeypatch.delenv("MEMORIA_IO_WORKERS", raising=False)
    plan = disk_speed._classify({"seek_penalty": None, "trim": None, "bus_type": "SAS"}, tmp_path, False)
    assert not plan["is_ssd"] and plan["workers"] == 2


def test_read_concurrency_override(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORIA_IO_WORKERS", "3")
    plan = disk_speed._classify({"seek_penalty": True, "bus_type": "USB"}, tmp_path, False)
    assert (plan["workers"], plan["video_workers"]) == (3, 1)
