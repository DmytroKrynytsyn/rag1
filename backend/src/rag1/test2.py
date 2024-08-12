
from pymilvus import MilvusClient

client = MilvusClient(
    uri="http://vector_db.local:19530"
)


res = client.list_partitions(collection_name="quick_setup")
print(res)

res = client.list_partitions(collection_name="quick_setup2")
print(res)
