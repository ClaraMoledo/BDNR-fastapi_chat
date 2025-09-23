from pathlib import Path
from dotenv import load_dotenv
import os

# Caminho raiz do projeto
ROOT = Path(__file__).resolve().parents[1]

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path=ROOT / ".env")

# Configurações principais
MONGO_URL: str = os.getenv("MONGO_URL", "")
MONGO_DB: str = os.getenv("MONGO_DB", "chatdb")
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

# Segurança: erro claro se a URL do Mongo não estiver definida
if not MONGO_URL:
    raise RuntimeError(
        "❌ Defina a variável MONGO_URL no arquivo .env (string de conexão do MongoDB Atlas)."
    )
