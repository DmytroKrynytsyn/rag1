from pymilvus import utility
from pymilvus import connections

# Connect to the Milvus server
connections.connect("default", host="vector_db.local", port="19530")

# List all collections
collections = utility.list_collections()

# Print the list of collections
print("Collections:", collections)