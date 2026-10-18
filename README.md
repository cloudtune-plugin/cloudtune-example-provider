# CloudTune Example Provider

CloudTune Example Provider is a sample media provider plugin for [Media Provider Server](https://github.com/cloudtune-music/media-provider-server).

It demonstrates how to extend Media Provider Server with custom media discovery and playback capabilities using the [Media Provider SDK](https://github.com/cloudtune-music/media-provider-sdk).

The plugin runs in an isolated Python environment managed by Media Provider Server.

## Features

- **Media Search** — Search for media tracks using keywords.
- **Track Information** — Retrieve track titles, artists, durations, and other available metadata.
- **Stream Resolution** — Resolve playable media streams.
- **Playback Integration** — Works with Media Provider Server's playback APIs.
- **Plugin Isolation** — Runs through the Media Provider Runtime in a separate process.
- **Easy Installation** — Install and manage the plugin through the Server's Web UI.

## Requirements

- Media Provider Server v0.1.0 or later
- Media Provider SDK v0.1.x
- Python 3.12 or later (for standalone development)

## Installation

### Option 1: Install via Web UI (Recommended)

1. Download the latest `.whl` file from the [Releases](https://github.com/cloudtune-music/cloudtune-example-provider/releases) page.
2. Open your Media Provider Server administration interface:

   `http://localhost:8000/admin/plugins`

3. Sign in using your administrator account.
4. Click **Install Plugin**.
5. Select the downloaded `.whl` file.
6. Click **Install** and wait for the installation to complete.
7. Enable the plugin if required.

The Server automatically manages the plugin installation, dependencies, and runtime environment.

### Option 2: Install via Plugin Directory

Copy the downloaded `.whl` file into the Server's plugin directory:

```text
plugins/
└── cloudtune_example_provider-0.1.0-py3-none-any.whl
```

For Docker Compose deployments, the host's `./plugins` directory is typically mounted to `/app/plugins` inside the Server container.

Restart Media Provider Server or use the plugin directory scan function to discover the plugin.

## Provider Configuration

After installation:

1. Open **Plugin Manager**.
2. Select **CloudTune Example Provider**.
3. Open the provider configuration section.
4. Create a new Provider Configuration.
5. Select the available provider entry point.
6. Enter the required settings, if any.
7. Save the configuration.

The provider is now available through Media Provider Server.

## Using with CloudTune Music

Once the plugin is installed and configured:

1. Open CloudTune Music.
2. Connect the application to your Media Provider Server.
3. Select the configured media provider, where applicable.
4. Search for media.
5. Select a track to start playback.

Media discovery and playback are handled through Media Provider Server.

## Development

Clone the repository:

```bash
git clone https://github.com/cloudtune-music/cloudtune-example-provider.git
cd cloudtune-example-provider
```

Install dependencies:

```bash
uv sync
```

Build the plugin:

```bash
uv build
```

The wheel package will be generated in the `dist/` directory.

Example output:

```text
dist/
└── cloudtune_example_provider-0.1.0-py3-none-any.whl
```

Upload the generated wheel to Media Provider Server for testing.

## Project Structure

```text
cloudtune-example-provider/
├── README.md
├── pyproject.toml
├── uv.lock
└── src/
    └── cloudtune_example_provider/
        ├── __init__.py
        ├── provider.py
        └── py.typed
```

## Architecture

The plugin integrates with Media Provider Server through the Media Provider SDK and Runtime.

```text
CloudTune Music
      |
      v
Media Provider Server
      |
      v
Plugin Manager
      |
      v
Media Provider Runtime
      |
      v
CloudTune Example Provider
      |
      v
Media Discovery & Stream Resolution
```

The Server manages plugin registration, configuration, execution, and communication with the client application.

## Notes

- This repository provides an example implementation of a media provider plugin.
- Media availability and playback depend on the underlying media sources.
- Some media streams may be unavailable or subject to access restrictions.
- Plugin functionality may change as external services evolve.
- Users are responsible for ensuring their use of media sources complies with applicable laws and service terms.

## Related Projects

- [Media Provider Server](https://github.com/cloudtune-music/media-provider-server)
- [Media Provider SDK](https://github.com/cloudtune-music/media-provider-sdk)
- [Media Provider Runtime](https://github.com/cloudtune-music/media-provider-runtime)

## License

This project is licensed under the MIT License.


## Disclaimer

CloudTune Example Provider is an independent, open-source example project intended for educational, development, and demonstration purposes.

This project does not host, store, or distribute any third-party media content. Media availability and accessibility depend on external sources and services.

This project is not affiliated with, endorsed by, or sponsored by any third-party content provider or service.

Users are solely responsible for ensuring that their use of this software complies with applicable laws, copyright regulations, and the terms of service of any third-party platforms they access.

The developers do not encourage or endorse copyright infringement, unauthorized access to protected content, or violations of third-party service terms.

This software is provided "AS IS", without warranties of any kind. The developers assume no responsibility for how the software is used or for any consequences arising from its use, to the extent permitted by applicable law.