
import importlib.util
import os

# =============================================google search==============================================
import requests
from bs4 import BeautifulSoup

class SearchEngine:
    def __init__(self):
        self.session = requests.Session()
        self.api_key = "AIzaSyCFILzxXFMP5A-M_mcRsCE7PHWtLImTMek"
        self.cse_id = "102e9afcad9db4f6a"  # Replace with your Google Custom Search Engine ID
        
    def search(self, keywords='quantum, algorithm, circuit', num_results=5):

        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': keywords,
            'key': self.api_key,
            'cx': self.cse_id,
            'num': num_results
        }
        
        response = self.session.get(search_url, params=params)
        results = response.json().get("items", [])
        search_results = []
        
        for result in results:
            url = result['link']
            try:
                page_response = self.session.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                page_response.raise_for_status()
                
                soup = BeautifulSoup(page_response.text, 'html.parser')
                text_content = '\n'.join([p.get_text() for p in soup.find_all('p')])
                
                if text_content:
                    search_results.append(f"search result from {url}: {text_content}")
            except requests.RequestException:
                continue
        
        return '\n'.join(search_results)


#===================================================RAG=====================================================
import os
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class RAG:
    def __init__(self, root_folder: str, index_file="faiss_index.bin", meta_file="file_metadata.json"):
        """
        初始化 RAG，支持嵌入索引的存储和加载
        :param root_folder: 量子算法数据库根目录
        :param index_file: FAISS 索引存储文件
        :param meta_file: 存储文件路径列表的 JSON
        """
        self.root_folder = root_folder
        self.index_file = index_file
        self.meta_file = meta_file
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  # 轻量级嵌入模型
        self.index = None
        self.files = []  # 存储文件路径
        self.file_embeddings = []  # 存储文件嵌入
        
        # 如果存在已保存的索引，则直接加载
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.load_index()
        else:
            self.build_index()
            self.save_index()

    def build_index(self):
        """
        遍历文件目录，提取路径和内容，构建嵌入索引
        """
        print("Building new FAISS index...")
        for dirpath, _, filenames in os.walk(self.root_folder):
            for file in filenames:
                full_path = os.path.join(dirpath, file)
                self.files.append(full_path)

                # 组合元数据：文件路径 + 文件名
                text = f"{full_path.replace(self.root_folder, '')} {file}"
                
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        text += " " + f.read()[:300]

                except Exception:
                    print(f'unable to process{full_path}')
                    pass  

                # 计算嵌入
                embedding = self.model.encode(text, convert_to_numpy=True)
                self.file_embeddings.append(embedding)
                print(f'successfully processed find_all{full_path}')

        # 创建 faiss 索引
        self.file_embeddings = np.array(self.file_embeddings, dtype=np.float32)
        self.index = faiss.IndexFlatL2(self.file_embeddings.shape[1])
        self.index.add(self.file_embeddings)
        print("Index built successfully.")

    def save_index(self):
        """
        保存 FAISS 索引和文件元数据
        """
        print("Saving index and metadata...")
        faiss.write_index(self.index, self.index_file)  # 保存 FAISS 索引
        with open(self.meta_file, "w") as f:
            json.dump(self.files, f)  # 保存文件路径
        print("Index saved.")

    def load_index(self):
        """
        加载已保存的 FAISS 索引和文件元数据
        """
        print("Loading existing index...")
        self.index = faiss.read_index(self.index_file)  # 读取 FAISS 索引
        with open(self.meta_file, "r") as f:
            self.files = json.load(f)  # 读取文件路径列表
        print("Index loaded successfully.")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        搜索最相关的文件
        :param query: 查询关键词
        :param top_k: 返回的文件数
        :return: (文件路径, 相似度) 的列表
        """
        query_embedding = self.model.encode(query, convert_to_numpy=True).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            results.append((self.files[idx], distance))
        
        return results


#=================================other tools===============================
def load_function_from_script(script_path, function_name):
    # 获取模块名（比如 script.py -> script）
    module_name = os.path.splitext(os.path.basename(script_path))[0]

    # 加载模块
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 返回你要的函数
    return getattr(module, function_name)
def clean_output(code):
    code=code.replace("```","")
    index = code.find("OPENQASM")
    if index != -1:
        return code[index:]
    else:
        return code

def extract_plan(text):
    start = text.find("<<THE PLAN>>")
    end = text.find("<<END OF PLAN>>")
    if start != -1 and end != -1:
        return text[start + len("<<THE PLAN>>"):end].strip()
    else:
        return None

def extract_code(text):
    start = text.find("<<THE CODE>>")
    end = text.find("<<END OF CODE>>")
    if start != -1 and end != -1:
        return text[start + len("<<THE CODE>>"):end].strip()
    else:
        return None

def load_algorithm_tools(algo):
    tool_descriptions = ""
    try:
        module_name = f"kernels.tools_descriptions.{algo}_tools_description"
        module = importlib.import_module(module_name)
        data = getattr(module, f"{algo}_tools_description")
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"No tool description available for {algo}") from e
    
    for func in data['functions']:
        tool_descriptions += f"- {func['name']}{func['signature']}\n  {func['description']}\n\n"
    return tool_descriptions
def clean_qasm_string(s):
    # 去掉 ``` 包裹
    s = s.strip().strip("`")
    # 找到 OPENQASM 开头的部分
    start_index = s.find("OPENQASM")
    if start_index != -1:
        return s[start_index:].strip()
    return s.strip()  # 如果没找到 OPENQASM，就返回处理后的原字符串


import re
from pathlib import Path

def calibrate(param_name: str, new_value: float, filename: str = "./backend_27q.inc"):

    path = Path(filename)
    text = path.read_text()

    pattern = rf"(const\s+float\s+{re.escape(param_name)}\s*=\s*)([0-9.+-eE]+)(\s*;)"
    repl = rf"\g<1>{new_value:.3f}\3"

    new_text, nsubs = re.subn(pattern, repl, text)
    if nsubs == 0:
        raise ValueError(f"Parameter {param_name} not found in {filename}")

    path.write_text(new_text)
    print(f"Updated {param_name} → {new_value:.3f} in {filename}")


def safe_read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def remove_json_comments(json_string: str) -> str:
    regex_pattern = r"\s*//.*"
    clean_lines = [re.sub(regex_pattern, "", line) for line in json_string.splitlines()]
    return "\n".join(clean_lines)

    
# Example usage:
if __name__ == "__main__":
    calibrate('x_len', '160dt',  "./test.inc")
    '''

    se = SearchEngine()
    results = se.search("grover algorithm circuit", num_results=3)
    print(results)
    '''
    # rag = RAG(root_folder="./QCircuitNet_Dataset-simplified")
    # results = rag.search("grover quantum 4 qubit full circuit", top_k=5)

    # for file, score in results:
    #     print(f"File: {file}, Score: {score}")

    #print(load_algorithm_tools('pe'))

