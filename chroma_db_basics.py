# export HNSWLIB_NO_NATIVE = 1
import chromadb

chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="my_collection")

collection.add(
    documents=["my name is Camilo", "my name is not Camilo"],
    metadatas=[{"source": "my name is true"}, {"source": "my name is false"}],
    ids=["id1", "id2"],
)


results = collection.query(query_texts=["This is a query document"], n_results=2)

print(results)
