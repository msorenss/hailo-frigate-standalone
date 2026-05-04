#!/usr/bin/env python3
"""Patch Frigate's hailo8l detector plugin for Hailo-10H.

This is adapted for the standalone image from the community add-on patch in
mikehailodev/frigate-hass-addons-h10. It keeps Frigate's public detector key as
`hailo8l` while allowing the plugin to auto-detect Hailo-10H hardware.
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


target = find_detector_plugin()
if target is None:
    print("ERROR: hailo8l.py not found; cannot patch Frigate", file=sys.stderr)
    sys.exit(1)

print(f"Patching {target} for Hailo-10H support")
with open(target, "r", encoding="utf-8") as file:
    src = file.read()

original = src

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
src = replace_once(src, old_constants, new_constants, "default model constants")

old_detect = '''\
                if "HAILO8L" in line:
                    return "hailo8l"
                elif "HAILO8" in line:
                    return "hailo8"'''
new_detect = '''\
                if "HAILO10H" in line or "HAILO10" in line:
                    return "hailo10h"
                elif "HAILO8L" in line:
                    return "hailo8l"
                elif "HAILO8" in line:
                    return "hailo8"'''
src = replace_once(src, old_detect, new_detect, "architecture detection")

old_extract = '''\
            if ARCH == "hailo8":
                return H8_DEFAULT_MODEL
            else:
                return H8L_DEFAULT_MODEL'''
new_extract = '''\
            if ARCH == "hailo10h":
                return H10_DEFAULT_MODEL
            elif ARCH == "hailo8":
                return H8_DEFAULT_MODEL
            else:
                return H8L_DEFAULT_MODEL'''
src = replace_once(src, old_extract, new_extract, "model-name selection")

old_prepare = '''\
                if ARCH == "hailo8":
                    self.download_model(H8_DEFAULT_URL, cached_model_path)
                else:
                    self.download_model(H8L_DEFAULT_URL, cached_model_path)'''
new_prepare = '''\
                if ARCH == "hailo10h":
                    self.download_model(H10_DEFAULT_URL, cached_model_path)
                elif ARCH == "hailo8":
                    self.download_model(H8_DEFAULT_URL, cached_model_path)
                else:
                    self.download_model(H8L_DEFAULT_URL, cached_model_path)'''
src = replace_once(src, old_prepare, new_prepare, "model download selection")

old_vdevice = '''\
        params = VDevice.create_params()
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN'''
new_vdevice = '''\
        params = VDevice.create_params()
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
        params.group_id = "SHARED"'''
src = replace_once(src, old_vdevice, new_vdevice, "shared VDevice group")

src = src.replace(
    "Hailo-8/Hailo-8L detector using HEF models and the HailoRT SDK",
    "Hailo-8/Hailo-8L/Hailo-10H detector using HEF models and the HailoRT SDK",
)
src = src.replace(
    'title="Hailo-8/Hailo-8L"',
    'title="Hailo-8/Hailo-8L/Hailo-10H"',
)

if src == original:
    print("ERROR: no changes applied; Frigate plugin may have changed", file=sys.stderr)
    sys.exit(1)

with open(target, "w", encoding="utf-8") as file:
    file.write(src)

print("hailo8l.py patched successfully")
