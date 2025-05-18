from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from rcon import Client
from config import Config
from commands import commands
import time
import json
import os
from flask_sqlalchemy import SQLAlchemy
import requests

db = SQLAlchemy()


class Mod(db.Model):
    __tablename__ = "mods"
    mod_id = db.Column(db.String, primary_key=True)
    workshop_id = db.Column(db.String, nullable=True)
    enabled = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "mod_id": self.mod_id,
            "workshop_id": self.workshop_id,
            "enabled": self.enabled,
        }


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
    import re

    match = re.search(r"id=(\d+)", collection_url_or_id)
    if match:
        collection_id = match.group(1)
    else:
        collection_id = collection_url_or_id.strip()
        if not collection_id.isdigit():
            raise ValueError("Invalid collection URL or ID")
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
    payload = {"collectioncount": 1, "publishedfileids[0]": collection_id}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"Steam API error: {resp.status_code}")
        data = resp.json()
        # Log the raw response for debugging
        print(f"Steam API response: {data}")
        if "response" not in data or "collectiondetails" not in data["response"]:
            raise Exception("Malformed Steam API response: missing 'collectiondetails'")
        details = data["response"]["collectiondetails"][0]
        if "children" not in details:
            raise Exception(
                "Malformed Steam API response: missing 'children' "
                "(is this a valid collection?)"
            )
        workshop_ids = [child["publishedfileid"] for child in details["children"]]
        return workshop_ids
    except Exception as e:
        print(f"Error fetching collection: {e}")
        raise


# Simple file-based cache for workshop details
WORKSHOP_CACHE_FILE = os.path.join(os.path.dirname(__file__), "workshop_cache.json")
CACHE_TTL = 60 * 60 * 12  # 12 hours


def load_workshop_cache():
    if os.path.exists(WORKSHOP_CACHE_FILE):
        try:
            with open(WORKSHOP_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_workshop_cache(cache):
    try:
        with open(WORKSHOP_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception:
        pass


def get_workshop_details_with_cache(wid):
    cache = load_workshop_cache()
    now = int(time.time())
    entry = cache.get(wid)
    if entry and (now - entry.get("timestamp", 0) < CACHE_TTL):
        return entry["details"]
    # Not cached or expired, fetch from Steam
    resp = requests.post(
        "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/",
        data={"itemcount": 1, "publishedfileids[0]": wid},
        timeout=10,
    )
    if resp.status_code == 200:
        data = resp.json()
        details = data["response"]["publishedfiledetails"][0]
        cache[wid] = {"details": details, "timestamp": now}
        save_workshop_cache(cache)
        return details
    return None


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pzmods.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

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
            # For each workshop_id, fetch mod ids
            from extract_mod_ids import extract_mod_ids_from_metadata

            mod_map = {}
            for wid in workshop_ids:
                try:
                    details = get_workshop_details_with_cache(wid)
                    if details:
                        desc = details.get("description", "")
                        title = details.get("title", "")
                        meta = details.get("metadata", "")
                        mod_ids = set()
                        # Try to extract Mod ID: ... (case-insensitive, allow underscore)
                        import re

                        modid_match = re.search(
                            r"Mod ?ID[:=]\s*([\w_\-]+)",
                            desc,
                            re.IGNORECASE,
                        )
                        if modid_match:
                            mod_ids.add(modid_match.group(1))
                        # Fallback to previous extraction logic
                        found = extract_mod_ids_from_metadata(desc)
                        mod_ids.update(found)
                        found = extract_mod_ids_from_metadata(meta)
                        mod_ids.update(found)
                        found = extract_mod_ids_from_metadata(title)
                        mod_ids.update(found)
                        if "requireditems" in details:
                            for req in details["requireditems"]:
                                req_title = req.get("title", "")
                                found = extract_mod_ids_from_metadata(req_title)
                                mod_ids.update(found)
                        mod_map[wid] = list(mod_ids)
                    else:
                        mod_map[wid] = []
                except Exception:
                    mod_map[wid] = []
            return jsonify({"workshop_ids": workshop_ids, "workshop_mod_map": mod_map})
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
                details = get_workshop_details_with_cache(wid)
                if details:
                    desc = details.get("description", "")
                    title = details.get("title", "")
                    meta = details.get("metadata", "")
                    # Try to extract Mod ID: ... (case-insensitive, allow underscore)
                    import re

                    modid_match = re.search(
                        r"Mod ?ID[:=]\s*([\w_\-]+)",
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

    @app.route("/mods", methods=["GET"])
    def get_mods():
        mods = Mod.query.all()
        return jsonify([m.to_dict() for m in mods])

    @app.route("/mods", methods=["POST"])
    def add_mod():
        data = request.get_json()
        mod_id = data.get("mod_id")
        workshop_id = data.get("workshop_id")
        enabled = data.get("enabled", True)
        if not mod_id:
            return jsonify({"error": "mod_id required"}), 400
        if Mod.query.get(mod_id):
            return jsonify({"error": "mod_id already exists"}), 400
        mod = Mod(mod_id=mod_id, workshop_id=workshop_id, enabled=enabled)
        db.session.add(mod)
        db.session.commit()
        return jsonify(mod.to_dict()), 201

    @app.route("/mods/<mod_id>", methods=["PATCH"])
    def update_mod(mod_id):
        mod = Mod.query.get(mod_id)
        if not mod:
            return jsonify({"error": "mod not found"}), 404
        data = request.get_json()
        if "workshop_id" in data:
            mod.workshop_id = data["workshop_id"]
        if "enabled" in data:
            mod.enabled = data["enabled"]
        db.session.commit()
        return jsonify(mod.to_dict())

    @app.route("/mods/<mod_id>", methods=["DELETE"])
    def delete_mod(mod_id):
        mod = Mod.query.get(mod_id)
        if not mod:
            return jsonify({"error": "mod not found"}), 404
        db.session.delete(mod)
        db.session.commit()
        return "", 204

    @app.route("/api/clear-cache", methods=["POST"])
    def clear_cache():
        try:
            if os.path.exists(WORKSHOP_CACHE_FILE):
                os.remove(WORKSHOP_CACHE_FILE)
            return jsonify({"status": "Cache cleared"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
