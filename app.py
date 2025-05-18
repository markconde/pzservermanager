import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from rcon import Client
from config import Config
from commands import commands

def parse_mods_and_workshop_ids(mod_ids_str, workshop_ids_str):
    mod_ids = mod_ids_str.split(';') if mod_ids_str else []
    workshop_ids = workshop_ids_str.split(';') if workshop_ids_str else []
    max_len = max(len(mod_ids), len(workshop_ids))
    # Pad lists with empty strings if needed
    mod_ids += [''] * (max_len - len(mod_ids))
    workshop_ids += [''] * (max_len - len(workshop_ids))
    return [
        {'mod_id': mod_id, 'workshop_id': workshop_id}
        for mod_id, workshop_id in zip(mod_ids, workshop_ids)
    ]

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.route('/', methods=['GET'])
    def index():
        return render_template("index.html", commands=commands)
    
    @app.route('/command', methods=['POST'])
    def run_command():
        cmd_key = request.form.get('command')
        cmd_info = commands.get(cmd_key)
        if not cmd_info:
            flash(f"Unknown command: {cmd_key}")
            return redirect(url_for('index'))
    
        # Build command string using parameters
        params = []
        for param in cmd_info['params']:
            value = request.form.get(param)
            if value:
                params.append(f'"{value}"')
        full_cmd = f"{cmd_key} " + " ".join(params) if params else f"{cmd_key}"
        
        try:
            with Client(app.config['RCON_HOST'],
                        app.config['RCON_PORT'],
                        passwd=app.config['RCON_PASSWORD']) as client:
                resp = client.run(full_cmd)
                flash(f"Command '{full_cmd}' executed. Response: {resp}")
        except Exception as e:
            flash(f"Error executing '{full_cmd}': {e}")
    
        return redirect(url_for('index'))

    @app.route('/parse-mods', methods=['POST'])
    def parse_mods():
        data = request.get_json()
        mod_ids = data.get('mod_ids', '')
        workshop_ids = data.get('workshop_ids', '')
        result = parse_mods_and_workshop_ids(mod_ids, workshop_ids)
        return jsonify(result)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)