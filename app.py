from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from rcon import Client
from config import Config
from commands import commands
import requests


def parse_mods_and_workshop_ids(mod_ids_str, workshop_ids_str):
    mod_ids = mod_ids_str.split(";") if mod_ids_str else []
    workshop_ids = workshop_ids_str.split(";") if workshop_ids_str else []
    max_len = max(len(mod_ids), len(workshop_ids))
    # Pad lists with empty strings if needed
    mod_ids += [""] * (max_len - len(mod_ids))
    workshop_ids += [""] * (max_len - len(workshop_ids))
    return [
        {"mod_id": mod_id, "publishedfileid": workshop_id}
        for mod_id, workshop_id in zip(mod_ids, workshop_ids)
    ]


def fetch_collection_workshop_ids(collection_url_or_id):
    """
    Given a Steam Workshop collection URL or ID,
    fetch the list of Workshop item IDs in the collection.
    Returns a list of workshop IDs as strings.
    """
    # Extract collection ID from URL or use as-is
    import re

    match = re.search(r"id=(\d+)", collection_url_or_id)
    if match:
        collection_id = match.group(1)
    else:
        # If only digits, treat as ID
        collection_id = collection_url_or_id.strip()
        if not collection_id.isdigit():
            raise ValueError("Invalid collection URL or ID")

    # Steam API endpoint for collection details
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
    payload = {"collectioncount": 1, "publishedfileids[0]": collection_id}
    resp = requests.post(url, data=payload, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"Steam API error: {resp.status_code}")
    data = resp.json()
    try:
        children = data["response"]["collectiondetails"][0]["children"]
        workshop_ids = [child["publishedfileid"] for child in children]
        return workshop_ids
    except Exception as e:
        raise Exception(f"Failed to parse Steam API response: {e}")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html", commands=commands)

    @app.route("/command", methods=["POST"])
    def run_command():
        cmd_key = request.form.get("command")
        cmd_info = commands.get(cmd_key)
        if not cmd_info:
            flash(f"Unknown command: {cmd_key}")
            return redirect(url_for("index"))

        # Build command string using parameters
        params = []
        for param in cmd_info["params"]:
            value = request.form.get(param)
            if value:
                params.append(f'"{value}"')
        full_cmd = f"{cmd_key} " + " ".join(params) if params else f"{cmd_key}"

        try:
            with Client(
                app.config["RCON_HOST"],
                app.config["RCON_PORT"],
                passwd=app.config["RCON_PASSWORD"],
            ) as client:
                resp = client.run(full_cmd)
                flash(f"Command '{full_cmd}' executed. Response: {resp}")
        except Exception as e:
            flash(f"Error executing '{full_cmd}': {e}")

        return redirect(url_for("index"))

    @app.route("/parse-mods", methods=["POST"])
    def parse_mods():
        data = request.get_json()
        mod_ids = data.get("mod_ids", "")
        workshop_ids = data.get("workshop_ids", "")
        result = parse_mods_and_workshop_ids(mod_ids, workshop_ids)
        return jsonify(result)

    @app.route("/api/collection", methods=["POST"])
    def api_collection():
        data = request.get_json()
        collection_url = data.get("collection_url")
        if not collection_url:
            return jsonify({"error": "Missing collection_url"}), 400
        try:
            workshop_ids = fetch_collection_workshop_ids(collection_url)
            return jsonify({"workshop_ids": workshop_ids})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/export", methods=["GET"])
    def api_export():
        ids = request.args.get("workshop_ids", "")
        ids = ids.replace(",", ";")
        workshop_ids = [i.strip() for i in ids.split(";") if i.strip()]
        from extract_mod_ids import extract_mod_ids_from_metadata

        mods = set()
        for wid in workshop_ids:
            try:
                import requests

                resp = requests.post(
                    "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/",
                    data={"itemcount": 1, "publishedfileids[0]": wid},
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    details = data["response"]["publishedfiledetails"][0]
                    desc = details.get("description", "")
                    title = details.get("title", "")
                    meta = details.get("metadata", "")
                    # Try to extract Mod ID: ... (case-insensitive, allow underscore)
                    import re

                    modid_match = re.search(
                        r"Mod ID[:=]\s*([\w_\-]+)",
                        desc,
                        re.IGNORECASE,
                    )
                    if modid_match:
                        mods.add(modid_match.group(1))
                        continue
                    # Fallback to previous extraction logic
                    found = extract_mod_ids_from_metadata(desc)
                    if not found:
                        found = extract_mod_ids_from_metadata(meta)
                    if not found:
                        found = extract_mod_ids_from_metadata(title)
                    if not found and "requireditems" in details:
                        for req in details["requireditems"]:
                            req_title = req.get("title", "")
                            found += extract_mod_ids_from_metadata(req_title)
                    mods.update(found)
            except Exception:
                continue
        # Remove empty strings and deduplicate
        mods = [m for m in set(mods) if m]
        return jsonify(
            {
                "Mods": ";".join(mods),
                "WorkshopItems": ";".join(workshop_ids),
            }
        )

    @app.route("/export", methods=["GET", "POST"])
    def export_page():
        return render_template("export.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
