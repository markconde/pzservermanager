# PZ Server Manager

The **PZ Server Manager** is a lightweight Flask-based web application designed to manage a Project Zomboid dedicated server. It connects to the server via the RCON protocol and provides a browser-based control panel for administrators to:

- **Issue quick server commands** (e.g., save world, restart, stop) with a single click.
- **Broadcast chat messages** to all players.
- **Run arbitrary RCON commands** via a custom input field and view responses instantly.
- **View and manage server settings** by accessing the server's configuration files.

## Features

- **Command Execution:** Execute predefined or custom RCON commands.
- **Server Settings Access:** Read server configuration files (e.g., `ServerOptions.ini`).
- **Dockerized Deployment:** Easily deployable as a Docker container.

---

## Prerequisites

- **Docker** and **Docker Compose** installed on the host machine.
- A running Project Zomboid dedicated server with RCON enabled.
- Access to the server's configuration directory.

---

## Installation and Usage

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/zomboid-rcon.git
cd zomboid-rcon
```

### 2. Configure the Environment
Create a `.env` file in the root directory with the following variables:

```properties
SECRET_KEY=<your-secret-key>
RCON_HOST=<zomboid-server-ip>
RCON_PORT=<zomboid-rcon-port>
RCON_PASSWORD=<zomboid-rcon-password>
APP_PORT=<webapp-port-mapping>
GAME_SERVER_CONFIG_FOLDER_PATH=<path-to-zomboid-config-folder>
GAME_SERVER_OPTIONS_FILENAME=<server-options-filename>
# Optional for Cloudflared:
CLOUDFLARE_TUNNEL_TOKEN=<your-cloudflare-tunnel-token>
```

### 3. Choose Your Deployment Method

By default, the Docker Compose file uses the prebuilt image from Docker Hub.  
If you want to build the image locally instead, comment out the `image:` line and uncomment the `build: .` line in `docker-compose.yaml` under the `zomboid-rcon` service.

### 4. Start the Application

#### Without Cloudflared (default)
```bash
docker compose up
```

#### With Cloudflared Tunnel (optional)
To expose your app securely via Cloudflare Tunnel, ensure you have set `CLOUDFLARE_TUNNEL_TOKEN` in your `.env` file, then run:
```bash
docker compose --profile cloudflared up
```
This will start both the app and the Cloudflared tunnel.

---

The application will be accessible at `http://<host-ip>:5000` (replace `<host-ip>` with your server's IP).

---

## Accessing the Application

1. Open your browser and navigate to `http://<host-ip>:5000`.
2. Use the web interface to:
   - Execute predefined commands.
   - Broadcast messages to players.
   - Run custom RCON commands.
   - View server settings.

---

## File Structure

```
zomboid-rcon/
├── Dockerfile                 # Docker build instructions
├── docker-compose.yaml        # Docker Compose configuration
├── requirements.txt           # Python dependencies
├── config.py                  # Flask app configuration
├── app.py                     # Main Flask application
├── commands.py                # Predefined RCON commands
├── templates/                 # HTML templates for the web interface
│   ├── index.html
│   └── settings.html
├── static/                    # Static assets (CSS, JS, images)
└── .env                       # Environment variables (not committed)
```

---

## Notes

- Ensure the Project Zomboid server has RCON enabled and is accessible from the machine running this app.
- The `GAME_SERVER_CONFIG_FOLDER_PATH` must point to the directory containing the server's configuration files (e.g., `ServerOptions.ini`).
- The `cloudflared` service is **optional** and only runs if you use the `cloudflared` profile.
- If you do not set the Cloudflare tunnel token or do not use the profile, the app will run as usual without Cloudflare Tunnel.

---

## Troubleshooting

- **Cannot connect to RCON:** Verify the `RCON_HOST`, `RCON_PORT`, and `RCON_PASSWORD` in the `.env` file.
- **Permission issues with configuration files:** Ensure the Docker container has read access to the mounted configuration directory.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.