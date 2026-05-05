# Frigate Hailo-10H Service

The Frigate service builds from [services/frigate-h10/Dockerfile](../services/frigate-h10/Dockerfile). It starts from `ghcr.io/blakeblackshear/frigate:0.17.1`, replaces the bundled HailoRT runtime with HailoRT 5.3.0, and applies [services/frigate-h10/hailo10h_patch.py](../services/frigate-h10/hailo10h_patch.py).

## Detector Configuration

Copy [config/frigate/config.yml.example](../config/frigate/config.yml.example) to `config/frigate/config.yml` and adjust it for your camera. The camera template reads its RTSP URL from `FRIGATE_CAMERA_RTSP_URL` in `.env`. Keep `.env` local because it contains camera credentials.

Use `hailo10h` on Hailo-10H hardware. The image also preserves the upstream `hailo8l` detector for Hailo-8L hardware:

```yaml
detectors:
  hailo10h:
    type: hailo10h
    device: PCIe
```

The build now creates a separate `hailo10h` plugin alongside the upstream `hailo8l` plugin. That keeps both detector types available instead of overloading `hailo8l` for two different device families.

## Model Configuration

The example uses a Hailo-10H YOLO HEF URL:

```yaml
model:
  width: 640
  height: 640
  input_tensor: nhwc
  input_pixel_format: rgb
  input_dtype: int
  model_type: yolo-generic
  labelmap_path: /labelmap/coco-80.txt
  path: https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v5.3.0/hailo10h/yolov8m.hef
```

You can also mount local HEF models under `/models` through the compose volume `./models/frigate:/models` and point `model.path` at that file.

## MQTT to Home Assistant

Home Assistant can stay on separate hardware. Configure Frigate MQTT to point at the broker used by Home Assistant:

```yaml
mqtt:
  enabled: true
  host: <mqtt-host-or-home-assistant-ip>
  port: 1883
  user: <mqtt-user>
  password: <mqtt-password>
```

If your broker runs as the Mosquitto add-on in Home Assistant, use the Home Assistant host IP and the MQTT credentials configured there.

## Ports

Defaults from [compose.yaml](../compose.yaml):

- `5000` - Frigate web UI
- `8971` - authenticated Frigate UI, if enabled by upstream image
- `8554` - RTSP restream
- `8555/tcp` and `8555/udp` - WebRTC
- `1984` - go2rtc API

## Shared Hailo Device

The build sets `params.group_id = "SHARED"` in both Hailo detector plugins. This is required so Frigate and the VLM container can both use the Hailo device concurrently.

## Implementation Notes

This split is a relatively small maintenance surface because Frigate auto-discovers detector plugins from the plugin directory and registers them by `type_key`. The standalone image uses that behavior to generate a `hailo10h.py` sibling plugin during build time while leaving the upstream `hailo8l.py` implementation largely intact.
