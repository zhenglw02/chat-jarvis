import logging
import chromadb
import os
from chromadb.utils import embedding_functions

from modules.long_memory.long_memory_interface import AbstractLongMemory, LongMemoryItem
from config import system_config


class ChromaLongMemory(AbstractLongMemory):
    def __init__(self):
        self._logger = None
        self._collection = None

    def init(self, logger: logging.Logger):
        self._logger = logger

        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=system_config.BRAIN_OPENAI_API_KEY,  # Replace with your own OpenAI API key
            model_name="text-embedding-ada-002"
        )
        # Create a new Chroma client with persistence enabled.
        persist_directory = os.path.join(os.path.split(os.path.abspath(__file__))[0], "../../",
                                         system_config.SYSTEM_DATA_PATH, "long_memory")

        client = chromadb.PersistentClient(path=persist_directory)

        # Create a new chroma collection
        collection_name = "long_memory_collection"
        self._collection = client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)

        # 如果是第一次运行，通过调一下search，让chroma加载一下依赖的模型文件
        self._logger.info("init chroma...")
        self.search(text="init message", n_results=1)
        self._logger.info("init chroma succeed")

    def save(self, items: [LongMemoryItem]):
        documents = []
        metadatas = []
        ids = []

        for item in items:
            documents.append(item.content)
            metadatas.append(item.metadata)
            ids.append(item.id)
        self._collection.add(
            documents=documents,
            metadatas=metadatas,  # filter on these!
            ids=ids,  # unique for each doc
        )

    def search(self, text: str, n_results: int, metadata_filter: dict = None) -> [LongMemoryItem]:
        results = self._collection.query(
            query_texts=[text],
            n_results=n_results,
            where=metadata_filter,  # optional filter
        )
        items = []
        for i in range(len(results.get('ids')[0])):
            items.append(LongMemoryItem.new(content="", metadata={}, id=""))

        for k, v in results.items():
            if k == 'ids':
                for i in range(len(v[0])):
                    items[i].id = v[0][i]
            elif k == 'metadatas':
                for i in range(len(v[0])):
                    items[i].metadata = v[0][i]
            elif k == 'documents':
                for i in range(len(v[0])):
                    items[i].content = v[0][i]
            elif k == 'distances':
                for i in range(len(v[0])):
                    items[i].distance = v[0][i]
        return items


if __name__ == "__main__":
    logger = logging.getLogger()

    m = ChromaLongMemory()
    m.init(logger)

    # i1 = LongMemoryItem.new(content="我喜欢吃鱼", metadata={"a": "b"}, id="id1")
    # i2 = LongMemoryItem.new(content="今天天气很好", metadata={"a": "b"}, id="id2")
    # i3 = LongMemoryItem.new(content="我叫郑利伟", metadata={"a": "b"}, id="id3")

    # m.save([i1, i2, i3])

    r = m.search("你应该叫我什么？", n_results=1)
    print("content: {}, distance: {}".format(r[0].content, r[0].distance))
