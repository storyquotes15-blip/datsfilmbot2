from flask import Flask
from threading import Thread
import os

# ===== Buat server kecil untuk keep-alive =====
app = Flask(__name__)  # pakai __name__ untuk standar Flask


@app.route("/")
def home():
    return "Bot is alive!"


def run_server(port: int) -> None:
    """Jalankan Flask server di port tertentu."""
    print(f"✅ Keep-alive server running on port {port}")
    app.run(host="0.0.0.0", port=port)


def keep_alive() -> None:
    """
    Jalankan server Flask di thread daemon agar bot tetap hidup.
    """
    port = int(os.environ.get("PORT", 8081))  # default port 8081
    thread = Thread(target=run_server, args=(port,), daemon=True)
    thread.start()


# ===== Supaya VSCode tidak kasih warning “function defined but not used” =====
if __name__ == "__main__":
    keep_alive()
