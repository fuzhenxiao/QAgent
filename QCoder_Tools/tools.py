
import importlib.util
import os


#===================================================RAG=====================================================
import os
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class RAG:
    def __init__(self, root_folder: str, index_file="faiss_index.bin", meta_file="file_metadata.json"):

        self.root_folder = root_folder
        self.index_file = index_file
        self.meta_file = meta_file
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  
        self.index = None
        self.files = []  
        self.file_embeddings = [] 
        

        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.load_index()
        else:
            self.build_index()
            self.save_index()

    def build_index(self):

        print("Building new FAISS index...")
        for dirpath, _, filenames in os.walk(self.root_folder):
            for file in filenames:
                full_path = os.path.join(dirpath, file)
                self.files.append(full_path)


                text = f"{full_path.replace(self.root_folder, '')} {file}"
                
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        text += " " + f.read()[:300]

                except Exception:
                    print(f'unable to process{full_path}')
                    pass  


                embedding = self.model.encode(text, convert_to_numpy=True)
                self.file_embeddings.append(embedding)
                print(f'successfully processed find_all{full_path}')


        self.file_embeddings = np.array(self.file_embeddings, dtype=np.float32)
        self.index = faiss.IndexFlatL2(self.file_embeddings.shape[1])
        self.index.add(self.file_embeddings)
        print("Index built successfully.")

    def save_index(self):

        print("Saving index and metadata...")
        faiss.write_index(self.index, self.index_file) 
        with open(self.meta_file, "w") as f:
            json.dump(self.files, f)  
        print("Index saved.")

    def load_index(self):

        print("Loading existing index...")
        self.index = faiss.read_index(self.index_file)
        with open(self.meta_file, "r") as f:
            self.files = json.load(f) 
        print("Index loaded successfully.")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:

        query_embedding = self.model.encode(query, convert_to_numpy=True).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            results.append((self.files[idx], distance))
        
        return results


#=================================other tools===============================
def load_function_from_script(script_path, function_name):

    module_name = os.path.splitext(os.path.basename(script_path))[0]


    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


    return getattr(module, function_name)
def clean_output(code):
    code=code.replace("```","")
    index = code.find("OPENQASM")
    if index != -1:
        return code[index:]
    else:
        return code



# Example usage:
if __name__ == "__main__":

    rag = RAG(root_folder="./QCircuitNet_Dataset-simplified")
    results = rag.search("tools for grover algorithm", top_k=5)

    for file, score in results:
        print(f"File: {file}, Score: {score}")

