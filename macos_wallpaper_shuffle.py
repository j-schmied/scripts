#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Improved wallpaper shuffle script for macOS.

Author: Jannik Schmied, 2023
"""
import argparse
import filetype
import matplotlib.pyplot as plt
import os
import random
import subprocess
import sys
import time

from appscript import app, mactypes
from collections import defaultdict


def notify(title: str, text: str, icon_path: str = "./assets/macos_beta.icns"):
    subprocess.run([
        "terminal-notifier",
        "-title", title,
        "-message", text,
        "-appIcon", icon_path
    ], check=True)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--path", "-p", help="Path to folder containing images", type=str, required=True)
    parser.add_argument("--interval", "-i", help="Interval in seconds between wallpaper changes", type=int, required=True, default=60)
    parser.add_argument("--restore", "-r", help="Restore previous wallpaper on exit", action="store_true")
    parser.add_argument("--analyze", "-a", help="Analyze image usage", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.isdir(args.path):
        notify("WallpaperShuffle", "Error: Path does not exist or is not a directory!")
        raise ValueError("[!] Path does not exist or is not a directory!")

    if args.restore:
        # Get current wallpaper
        print("[*] Saving current wallpaper")
        current_wallpaper = app('Finder').desktop_picture.get()

    images: list = [image for image in [file for file in os.listdir(args.path) if not os.path.isdir(os.path.join(args.path, file))] if filetype.is_image(os.path.join(args.path, image))]
    total_wallpapers = len(images)

    if total_wallpapers == 0:
        notify("WallpaperShuffle", "Error: No images found in specified directory!")
        raise ValueError("[!] No images found in specified directory!")

    wallpaper_counter: int = 0
    img_name_buf: int = 0
    img_counts = defaultdict(int)

    print("[*] Starting wallpaper shuffle. Press CTRL+C to stop.")
    notify("WallpaperShuffle", "Starting wallpaper shuffle. Press CTRL+C to stop.")

    while True:
        try:
            # Get random image from folder
            image = random.choice(images)

            # Set wallpaper
            app('Finder').desktop_picture.set(mactypes.File(os.path.join(args.path, image)))
            print(f"[i] Current wallpaper: {image.ljust(img_name_buf)}", end="\r", flush=True)

            # Increment wallpaper counter and sleep for interval
            img_name_buf = len(image)
            wallpaper_counter += 1
            img_counts[image] += 1

            # Update images folder
            images = [image for image in [file for file in os.listdir(args.path) if not os.path.isdir(os.path.join(args.path, file))] if filetype.is_image(os.path.join(args.path, image))]
            if total_wallpapers != len(images):
                print(f"[i] Updated images (Total: {total_wallpapers} -> {len(images)})")
                notify("WallpaperShuffle", f"Updated images (Total: {total_wallpapers} -> {len(images)})")
                total_wallpapers = len(images)

            time.sleep(args.interval)

        except KeyboardInterrupt:
            print(f"\n[i] Stopped. Shuffled {wallpaper_counter} wallpapers.")
            break

        except Exception as e:
            notify("WallpaperShuffle", f"Error: {e}")
            continue

    if args.restore:
        # Reset wallpaper
        print("[*] Restoring initial wallpaper")
        app('Finder').desktop_picture.set(current_wallpaper)

    if args.analyze:
        mean_usage = sum(img_counts.values()) / len(img_counts)
        std_deviation = (sum((x - mean_usage) ** 2 for x in img_counts.values()) / len(img_counts)) ** 0.5

        print(f"[i] Mean Usage: {mean_usage}")
        print(f"[i] Standard Deviation: {std_deviation}")

        plt.bar(img_counts.keys(), img_counts.values())
        plt.xlabel('Images')
        plt.ylabel('Usage Count')
        plt.title('Histogram of Image Usage')
        plt.xticks(rotation=90)
        plt.show()

    print("[*] Done. Exiting.")
    sys.exit(0)


if __name__ == "__main__":
    main()
