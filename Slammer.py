import threading
import time
import os

# ---------- CPU STRESS ----------
def cpu_stress(stop_event):
    while not stop_event.is_set():
        x = 0
        for i in range(5_000_000):
            x += i * i


# ---------- RAM STRESS ----------
def ram_stress(size_gb, stop_event):
    print(f"[+] Allocating {size_gb} GB RAM")

    block_size = 1024 * 1024  # 1MB
    num_blocks = size_gb * 1024

    data = []

    try:
        for i in range(num_blocks):
            block = bytearray(block_size)

            # force memory write
            for j in range(0, len(block), 4096):
                block[j] = 1

            data.append(block)

            if i % 512 == 0:
                print(f"[+] RAM: {i // 1024} GB allocated")

        print("[+] RAM allocation complete")

        while not stop_event.is_set():
            for block in data:
                block[0] = (block[0] + 1) % 256
            time.sleep(0.1)

    except MemoryError:
        print("[!] RAM limit hit")


# ---------- DISK STRESS ----------
def disk_stress(stop_event):
    filename = "temp_stress_file.bin"
    print("[+] Starting disk stress")

    try:
        with open(filename, "wb") as f:
            while not stop_event.is_set():
                f.write(os.urandom(1024 * 1024))  # 1MB writes
                f.flush()
    except Exception as e:
        print(f"[!] Disk error: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)


# ---------- MAIN ----------
def main():
    duration = 60   # seconds
    ram_gb = 16     # change this safely

    stop_event = threading.Event()
    threads = []

    # CPU threads (based on cores)
    cpu_count = os.cpu_count() or 4

    for _ in range(cpu_count):
        t = threading.Thread(target=cpu_stress, args=(stop_event,))
        t.start()
        threads.append(t)

    # RAM thread
    t_ram = threading.Thread(target=ram_stress, args=(ram_gb, stop_event))
    t_ram.start()
    threads.append(t_ram)

    # Disk thread
    t_disk = threading.Thread(target=disk_stress, args=(stop_event,))
    t_disk.start()
    threads.append(t_disk)

    print(f"[+] Running full stress for {duration} seconds...")
    time.sleep(duration)

    print("[+] Stopping stress test...")
    stop_event.set()

    for t in threads:
        t.join()

    print("[+] Done.")


if __name__ == "__main__":
    main()