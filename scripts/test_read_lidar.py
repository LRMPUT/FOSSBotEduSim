#!/usr/bin/env python3

import time
import traceback
# Requires rplidar-roboticia package
from rplidar import RPLidar
import csv

PORT_NAME = "/dev/ttyUSB0"

def run():
    lidar = None

    try:
        print("Connecting to RPLIDAR...")
        lidar = RPLidar(PORT_NAME)

        # Device information
        print("\n=== DEVICE INFO ===")
        info = lidar.get_info()
        print(f"Model:         {info['model']}")
        print(f"Firmware:      {info['firmware'][0]}.{info['firmware'][1]}")
        print(f"Hardware:      {info['hardware']}")
        print(f"Serial Number: {info['serialnumber']}")

        # Health information
        print("\n=== HEALTH ===")
        health = lidar.get_health()
        print(f"Status: {health[0]}")
        print(f"Error:  {health[1]}")

        print("\nStarting scan...")
        print("Press Ctrl+C to stop.\n")

        # Give the motor a moment to stabilize
        time.sleep(2)

        with open('lidar_data.csv', mode='w', newline='') as csv_file:
            fieldnames = ['scan_num', 'quality', 'angle', 'distance']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for scan_num, scan in enumerate(lidar.iter_scans()):

                distances = [distance for quality, angle, distance in scan]

                if distances:
                    min_dist = min(distances)
                    max_dist = max(distances)
                    avg_dist = sum(distances) / len(distances)
                else:
                    min_dist = max_dist = avg_dist = 0

                print("=" * 70)
                print(f"SCAN #{scan_num}")
                print(f"Points captured: {len(scan)}")
                print(f"Min distance:    {min_dist:.1f} mm")
                print(f"Max distance:    {max_dist:.1f} mm")
                print(f"Avg distance:    {avg_dist:.1f} mm")

                print("\nFirst 10 measurements:")
                for quality, angle, distance in scan[:10]:
                    print(
                        f"  Angle={angle:7.2f}° "
                        f"Distance={distance:8.1f} mm "
                        f"Quality={quality}"
                    )

                print()

                # Write scan data to CSV
                for quality, angle, distance in scan:
                    writer.writerow({
                        'scan_num': scan_num,
                        'quality': quality,
                        'angle': angle,
                        'distance': distance
                    })

                # Stop after 50 rotations for testing
                if scan_num >= 49:
                    print("Test complete.")
                    csv_file.close()
                    break

    except KeyboardInterrupt:
        print("\nStopped by user.")

    except Exception:
        print("\nERROR:")
        traceback.print_exc()

    finally:
        if lidar is not None:
            print("\nStopping lidar...")
            try:
                lidar.stop()
            except Exception:
                pass

            try:
                lidar.stop_motor()
            except Exception:
                pass

            try:
                lidar.disconnect()
            except Exception:
                pass

            print("Disconnected.")


if __name__ == "__main__":
    run()
