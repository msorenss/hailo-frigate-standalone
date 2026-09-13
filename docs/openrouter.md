# OpenRouter GenAI for Frigate

Frigate 0.18 can connect to OpenRouter through its existing OpenAI-compatible GenAI provider. No Frigate source patch or additional Python package is required.

OpenRouter receives the images that Frigate submits for descriptions or chat. Choose a model and retention policy appropriate for the sensitivity of your camera data. OpenRouter requests may incur usage charges.

## API Key

Create an API key in OpenRouter and put it in the local `.env` file:

```dotenv
FRIGATE_OPENROUTER_API_KEY=<your-openrouter-api-key>
```

Do not put the real key in `compose.yaml` or `config/frigate/config.yml`. Compose forwards it to the Frigate container, and Frigate resolves the `{FRIGATE_OPENROUTER_API_KEY}` placeholder at startup.

## Provider Configuration

Add this top-level block to `config/frigate/config.yml`:

```yaml
genai:
  openrouter:
    provider: openai
    base_url: https://openrouter.ai/api/v1
    api_key: "{FRIGATE_OPENROUTER_API_KEY}"
    model: google/gemini-2.5-flash
    roles:
      - descriptions
      - chat
    runtime_options:
      max_tokens: 300
```

The model slug is an example, not a required model. Select a current OpenRouter model that supports image input. Frigate chat also needs tool calling, while review summaries may need structured output support. Verify those capabilities and pricing in the [OpenRouter model catalog](https://openrouter.ai/models).

OpenRouter's attribution headers are optional. To enable them, add OpenAI client headers under the provider:

```yaml
    provider_options:
      default_headers:
        HTTP-Referer: https://example.com
        X-OpenRouter-Title: Frigate
```

## Object Descriptions

Enable generation only for the object types that should leave the local system:

```yaml
objects:
  track:
    - person
    - car
  genai:
    enabled: true
    objects:
      - person
      - car
```

Frigate sends a request when a matching tracked object ends. Keep this disabled initially if the camera is busy, because every generated description can create a billable request.

## Validation

Validate the Compose model without making an OpenRouter request:

```bash
docker compose --env-file .env -f compose.yaml config --quiet
```

After adding the provider configuration, validate it with the same Frigate image used by this repository:

```bash
docker compose --env-file .env -f compose.yaml run --rm --no-deps \
  --entrypoint python3 frigate-h10 -m frigate --validate-config
```

Then restart Frigate and inspect its logs:

```bash
docker compose --env-file .env -f compose.yaml up -d frigate-h10
docker compose --env-file .env -f compose.yaml logs --tail=100 frigate-h10
```

A successful config validation does not call OpenRouter. The first chat or generated description is the first end-to-end API test and may be billable.