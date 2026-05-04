# Hailo VLM Chat Service

The VLM service builds from [services/hailo-vlm/Dockerfile](../services/hailo-vlm/Dockerfile). It installs HailoRT packages locally, then fetches the upstream add-on application from `mikehailodev/hailo-vlm-addon` at image build time.

## Configuration

The upstream `run.sh` reads `/data/options.json`. Copy [config/vlm/options.json.example](../config/vlm/options.json.example) to `config/vlm/options.json`; Compose mounts that local ignored file to `/data/options.json`.

Example:

```json
{
  "camera_source": "rtsp://user:password@192.168.1.50:554/stream1",
  "max_tokens": 200,
  "temperature": 0.1,
  "default_prompt": "Describe the image",
  "system_prompt": "You are a helpful assistant that analyzes images and answers questions about them."
}
```

RTSP sources are recommended for a clean first deployment. USB cameras are supported, but you must add the matching `/dev/video*` mapping to [compose.yaml](../compose.yaml).

## VLM Model Setup

Mount VLM HEF files under `./models/vlm`, which appears as `/media` in the container.

The upstream server searches common paths such as `/data`, `/media`, `/share`, and the container home. File names containing `vlm` or `qwen` are preferred by the model discovery logic.

Download a Hailo-10H VLM HEF from the Hailo Model Zoo / Developer Zone. The upstream add-on recommends Qwen2-VL-2B-Instruct as the first model to try because it is small enough for this class of device while still giving useful scene descriptions.

Example file:

```text
models/vlm/Qwen2-VL-2B-Instruct.hef
```

After copying the file, restart the VLM service:

```bash
sudo docker compose --env-file .env -f compose.yaml restart hailo-vlm
```

Then check that the logs no longer say `No VLM HEF file found`:

```bash
sudo docker compose --env-file .env -f compose.yaml logs --tail=100 hailo-vlm
```

## API and UI

Default URL:

```text
http://<pi>:8099/
```

Useful endpoints:

- `GET /api/status`
- `GET /video_feed`
- `POST /api/capture`
- `POST /api/ask`
- `POST /api/resume`

If HailoRT or the HEF model is unavailable, the upstream app may start in demo/fallback mode. That is useful for checking camera and UI wiring, but it is not real Hailo inference.

## Home Assistant Integration

Because this repo runs standalone on a different Pi, Home Assistant should call the Pi directly instead of using Home Assistant add-on ingress URLs.

Replace `<pi-ip>` with this Pi's IP address.

### REST Commands

Add to Home Assistant `configuration.yaml`:

```yaml
rest_command:
  hailo_vlm_capture:
    url: "http://<pi-ip>:8099/api/capture"
    method: POST
    content_type: "application/json"

  hailo_vlm_ask:
    url: "http://<pi-ip>:8099/api/ask"
    method: POST
    content_type: "application/json"
    payload: '{"prompt": "{{ prompt }}"}'

  hailo_vlm_resume:
    url: "http://<pi-ip>:8099/api/resume"
    method: POST
```

### Status Sensor

```yaml
sensor:
  - platform: rest
    name: "Hailo VLM Status"
    resource: "http://<pi-ip>:8099/api/status"
    value_template: >
      {% if value_json.hailo_device and value_json.camera_ok %}
        ready
      {% elif value_json.camera_ok %}
        no_hailo
      {% elif value_json.hailo_device %}
        no_camera
      {% else %}
        offline
      {% endif %}
    json_attributes:
      - hailo_available
      - hailo_device
      - camera_ok
      - camera_source
    scan_interval: 30
```

### MJPEG Camera Entity

```yaml
camera:
  - platform: mjpeg
    name: "Hailo VLM Camera"
    mjpeg_url: "http://<pi-ip>:8099/video_feed"
    still_image_url: "http://<pi-ip>:8099/video_feed?snapshot=1"
```

### Dashboard Card

```yaml
type: iframe
url: "http://<pi-ip>:8099/"
aspect_ratio: "4:3"
title: Hailo VLM Chat
```
