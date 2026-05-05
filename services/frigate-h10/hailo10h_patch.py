#!/usr/bin/env python3
"""Expose separate hailo8l and hailo10h detector plugins in Frigate.

The upstream Frigate image ships only a hailo8l plugin. This script keeps that
plugin intact apart from enabling a shared VDevice group, and generates a new
hailo10h plugin beside it for Hailo-10H hardware.
"""

import os
import sys

SEARCH_PATHS = [
    "/opt/frigate/frigate/detectors/plugins/hailo8l.py",
    "/usr/local/lib/python3.11/dist-packages/frigate/detectors/plugins/hailo8l.py",
]


def find_detector_plugin():
    for path in SEARCH_PATHS:
        if os.path.exists(path):
            return path

    for root, _dirs, files in os.walk("/opt"):
        if "hailo8l.py" in files and "detectors" in root:
            return os.path.join(root, "hailo8l.py")

    return None


def replace_once(source, old, new, label):
    if old not in source:
        print(f"ERROR: patch target not found: {label}", file=sys.stderr)
        sys.exit(1)
    return source.replace(old, new, 1)


def add_shared_group(source):
    if 'params.group_id = "SHARED"' in source:
        return source

    old_vdevice = '''\
        params = VDevice.create_params()
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN'''
    new_vdevice = '''\
        params = VDevice.create_params()
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
        params.group_id = "SHARED"'''
    return replace_once(source, old_vdevice, new_vdevice, "shared VDevice group")


def build_hailo10h_plugin(source):
    h10_source = add_shared_group(source)

    h10_source = replace_once(
        h10_source,
        'DETECTOR_KEY = "hailo8l"',
        'DETECTOR_KEY = "hailo10h"',
        "hailo10h detector key",
    )

    old_constants = (
        'H8L_DEFAULT_URL = "https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/'
        'ModelZoo/Compiled/v2.14.0/hailo8l/yolov6n.hef"'
    )
    new_constants = (
        'H8L_DEFAULT_URL = "https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/'
        'ModelZoo/Compiled/v2.14.0/hailo8l/yolov6n.hef"\n'
        'H10_DEFAULT_MODEL = "yolov6n.hef"\n'
        'H10_DEFAULT_URL = "https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/'
        'ModelZoo/Compiled/v2.15.0/hailo10h/yolov6n.hef"'
    )
    h10_source = replace_once(
        h10_source,
        old_constants,
        new_constants,
        "hailo10h default model constants",
    )

    old_detect = '''\
                if "HAILO8L" in line:
                    return "hailo8l"
                elif "HAILO8" in line:
                    return "hailo8"'''
    new_detect = '''\
                if "HAILO10H" in line or "HAILO10" in line:
                    return "hailo10h"'''
    h10_source = replace_once(
        h10_source,
        old_detect,
        new_detect,
        "hailo10h architecture detection",
    )

    h10_source = replace_once(
        h10_source,
        '        ARCH = detect_hailo_arch()',
        '        ARCH = detect_hailo_arch()\n'
        '        if ARCH != "hailo10h":\n'
        '            raise RuntimeError(\n'
        '                f"Configured hailo10h detector on unsupported Hailo architecture: {ARCH}"\n'
        '            )',
        "hailo10h architecture validation",
    )

    old_extract = '''\
            if ARCH == "hailo8":
                return H8_DEFAULT_MODEL
            else:
                return H8L_DEFAULT_MODEL'''
    new_extract = '''\
            return H10_DEFAULT_MODEL'''
    h10_source = replace_once(
        h10_source,
        old_extract,
        new_extract,
        "hailo10h model-name selection",
    )

    old_prepare = '''\
                if ARCH == "hailo8":
                    self.download_model(H8_DEFAULT_URL, cached_model_path)
                else:
                    self.download_model(H8L_DEFAULT_URL, cached_model_path)'''
    new_prepare = '''\
                self.download_model(H10_DEFAULT_URL, cached_model_path)'''
    h10_source = replace_once(
        h10_source,
        old_prepare,
        new_prepare,
        "hailo10h model download selection",
    )

    return h10_source


target = find_detector_plugin()
if target is None:
    print("ERROR: hailo8l.py not found; cannot patch Frigate", file=sys.stderr)
    sys.exit(1)

plugin_dir = os.path.dirname(target)
h10_target = os.path.join(plugin_dir, "hailo10h.py")

with open(target, "r", encoding="utf-8") as file:
    original_source = file.read()

patched_h8l = add_shared_group(original_source)
patched_h10 = build_hailo10h_plugin(original_source)

with open(target, "w", encoding="utf-8") as file:
    file.write(patched_h8l)

with open(h10_target, "w", encoding="utf-8") as file:
    file.write(patched_h10)

print(f"Patched {target} for shared Hailo access")
print(f"Created {h10_target} for Hailo-10H detection")
