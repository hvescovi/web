import os

from .configuracoes import create_app
from .rotas import registrar_rotas

app = create_app()
registrar_rotas(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)

