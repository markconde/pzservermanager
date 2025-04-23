# Project Zomboid RCON Manager

The **Project Zomboid RCON Manager** is a lightweight Flask-based web application designed to manage a Project Zomboid dedicated server. It connects to the server via the RCON protocol and provides a browser-based control panel for administrators to:

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
```

- **`SECRET_KEY`**: Secret key for Flask session management.
- **`RCON_HOST`**: IP address of the Project Zomboid server.
- **`RCON_PORT`**: Port for the RCON service.
- **`RCON_PASSWORD`**: Password for the RCON service.
- **`APP_PORT`**: Port mapping for the web application (e.g., `5000:5000`).
- **`GAME_SERVER_CONFIG_FOLDER_PATH`**: Path to the Zomboid server's configuration folder.
- **`GAME_SERVER_OPTIONS_FILENAME`**: Name of the server options file (e.g., `ServerOptions.ini`).

### 3. Build and Run the Docker Container
Run the following command to build and start the RCON Manager:
```bash
docker-compose up --build
```

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

---

## Troubleshooting

- **Cannot connect to RCON:** Verify the `RCON_HOST`, `RCON_PORT`, and `RCON_PASSWORD` in the `.env` file.
- **Permission issues with configuration files:** Ensure the Docker container has read access to the mounted configuration directory.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.