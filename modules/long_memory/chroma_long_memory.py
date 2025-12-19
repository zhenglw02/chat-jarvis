import logging
import chromadb
import os
from chromadb.utils import embedding_functions

from modules.long_memory.long_memory_interface import AbstractLongMemory, LongMemoryItem
from config import system_config

from recorder import recorder_manager
from recorder.recorder_interface import RecordItem
from consts.const import *


class ChromaLongMemory(AbstractLongMemory):
    def __init__(self):
        self._logger = None
        self._collection = None

    def init(self, logger: logging.Logger):
        self._logger = logger

        # openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        #     api_key=system_config.LONG_MEMORY_OPENAI_API_KEY,  # Replace with your own OpenAI API key
        #     api_base=system_config.LONG_MEMORY_OPENAI_API_BASE,
        #     model_name=system_config.LONG_MEMORY_OPENAI_MODEL
        # )
        # Create a new Chroma client with persistence enabled.
        persist_directory = os.path.join(os.path.split(os.path.abspath(__file__))[0], "../../",
                                         system_config.SYSTEM_DATA_PATH, "long_memory")

        client = chromadb.PersistentClient(path=persist_directory)

        # Create a new chroma collection
        collection_name = "long_memory_collection"
        self._collection = client.get_or_create_collection(name=collection_name)

        # 如果是第一次运行，通过调一下search，让chroma加载一下依赖的模型文件
        self._logger.info("init chroma...")
        self.search(text="init message", n_results=1)
        self._logger.info("init chroma succeed")

    def save(self, items: [LongMemoryItem]):
        if items is None or len(items) == 0:
            return

        documents = []
        metadatas = []
        ids = []

        to_delete_ids = []
        for item in items:
            # 从记忆中检索相似的内容，删掉旧的，保留新的，避免保存过多重复记忆
            old_memories = self.search(text=item.content, n_results=5)
            for old_memory in old_memories:
                if old_memory.distance < 0.2:
                    to_delete_ids.append(old_memory.id)
                else:
                    break
            documents.append(item.content)
            metadatas.append(item.metadata)
            ids.append(item.id)

        self.delete(to_delete_ids)
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

    def delete(self, ids: list):
        if ids is None or len(ids) == 0:
            return
        self._collection.delete(ids=ids)
