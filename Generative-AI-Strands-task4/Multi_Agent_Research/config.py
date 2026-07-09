import os
from dotenv import load_dotenv
load_dotenv()  

#----------------------------- Paths ---------------------------#
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
VECTOR_DB_DIR = os.path.join(ROOT_DIR, "vector_db")  
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "knowledge_base")
import os
from dotenv import load_dotenv
load_dotenv()

#----------------------------- Paths ---------------------------#
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
VECTOR_DB_DIR = os.path.join(ROOT_DIR, "vector_db")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "knowledge_base")


#------------------------------ AWS / Bedrock ------------------#
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
EMBED_MODEL_ID = os.environ.get("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
EMBED_DIM = int(os.environ.get("EMBED_DIM", "1024"))  # Titan v2 supports 256 / 512 / 1024
AGENT_MODEL_ID = os.environ.get("AGENT_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
AGENT_TEMPERATURE = float(os.environ.get("AGENT_TEMPERATURE", "0.2"))

# --------------------Chunking / retrieval----------------------#

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "800"))       
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "150"))  
DEFAULT_TOP_K = int(os.environ.get("DEFAULT_TOP_K", "4"))
MAX_RETRIEVAL_ATTEMPTS = int(os.environ.get("MAX_RETRIEVAL_ATTEMPTS", "3"))