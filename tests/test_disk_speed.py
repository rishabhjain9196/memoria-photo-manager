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


def test_paced_map_reads_in_folder_order_within_the_drive_limit(tmp_path, monkeypatch):
    import threading
    import time
    monkeypatch.setenv("MEMORIA_IO_WORKERS", "1")
    disk_speed.reset_cache()
    try:
        paths = [tmp_path / name for name in ("b/2.jpg", "a/1.jpg", "b/1.jpg", "a/2.jpg")]
        active, peak, order, lock = [0], [0], [], threading.Lock()

        def read(path):
            with lock:
                active[0] += 1
                peak[0] = max(peak[0], active[0])
                order.append(path)
            time.sleep(0.01)
            with lock:
                active[0] -= 1
            return path.name

        assert list(disk_speed.paced_map(read, paths, lambda p: p, "Test")) == ["1.jpg", "2.jpg", "1.jpg", "2.jpg"]
        assert peak[0] == 1 and order == sorted(paths, key=lambda p: str(p).lower())

        busy, peak_cpu = [0], [0]

        def decode(path, gate):
            with gate:
                pass                          # the read: one at a time
            with lock:
                busy[0] += 1
                peak_cpu[0] = max(peak_cpu[0], busy[0])
            time.sleep(0.05)                  # CPU work outside the gate overlaps
            with lock:
                busy[0] -= 1

        list(disk_speed.paced_map(decode, paths, lambda p: p, "Test", hold_gate=False))
        assert peak_cpu[0] > 1
    finally:
        disk_speed.reset_cache()
