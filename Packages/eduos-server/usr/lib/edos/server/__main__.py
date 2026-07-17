import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import configparser

CONFIG_PATH = "/etc/edos/server.conf"


def load_config():
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": False,
        "db_path": "/var/lib/edos/server.db",
    }
    parser = configparser.ConfigParser()
    try:
        parser.read(CONFIG_PATH)
        if parser.has_section("server"):
            config["host"] = parser.get("server", "host", fallback="0.0.0.0")
            config["port"] = parser.getint("server", "port", fallback=8000)
            config["debug"] = parser.getboolean("server", "debug", fallback=False)
        if parser.has_section("database"):
            config["db_path"] = parser.get(
                "database", "db_path", fallback="/var/lib/edos/server.db"
            )
    except Exception:
        pass
    return config


def main():
    config = load_config()
    host = config["host"]
    port = config["port"]
    debug = config["debug"]

    os.environ["EDOS_DB_PATH"] = config["db_path"]

    import uvicorn

    print(f"EduOS Server starting on {host}:{port}")
    uvicorn.run("api_server:app", host=host, port=port, reload=debug)


if __name__ == "__main__":
    main()
