
from tools import RAG
from LLM import LLM_model


class RAG_Agent(object):

    def __init__(self, llm, num_of_examples, RAG):
        self.llm = llm
        self.num_of_examples = num_of_examples
        self.RAG = RAG
    def get_key_words(self, question=''):
        """
        Use LLM to extract concise keywords from the question for semantic search.

        """

        top_paths = self.RAG.search(question, top_k=self.num_of_examples)

        prompt = (
                "Analyze the path below, tell what kind of quantum algorithm it involves\n\n"
                "give me the algorithm name directly, nothing else is needed"
                f"path:\n{top_paths[0]}"
            )



        keyword_str = self.llm.generate(prompt, role="prompt", max_tokens=20)# this is a vulnerable writing style, will be replaced later
        print(keyword_str)
        return keyword_str.strip()


    def get_key_words_for_qasm(self, question=''):
        """
        Use LLM to extract concise keywords from the question for semantic search.

        """

        top_paths = self.RAG.search(question, top_k=self.num_of_examples)

        prompt = (
                "Analyze the path below, tell what kind of quantum algorithm it involves\n\n"
                "give me the algorithm name directly, nothing else is needed"
                f"path:\n{top_paths[0]}"
            )



        keyword_str = self.llm.generate(prompt, role="prompt", max_tokens=20)# this is a vulnerable writing style, will be replaced later

        keyword_str+=',qasm_circuit'
        print(keyword_str)
        return keyword_str.strip()

    def get_key_words_for_full_circuit(self, question=''):
        """
        Use LLM to extract concise keywords from the question for semantic search.

        """

        top_paths = self.RAG.search(question, top_k=self.num_of_examples)

        prompt = (
                "Analyze the path below, tell what kind of quantum algorithm it involves\n\n"
                "give me the algorithm name directly, nothing else is needed"
                f"path:\n{top_paths[0]}"
            )



        keyword_str = self.llm.generate(prompt, role="prompt", max_tokens=30)# this is a vulnerable writing style, will be replaced later

        keyword_str+=',full_circuit'
        print(keyword_str)
        return keyword_str.strip()


    def get_most_relevant_qasm(self, question=''):
        """
        Use LLM to extract concise keywords from the question for semantic search.
        """

        keyword_query = self.get_key_words(question)
        top_paths = self.RAG.search(keyword_query , top_k=10)

        for i in range(0,len(top_paths)):
            print(str(i)+'.\n'+top_paths[i][0])


        prompt = (
                f"Analyze the paths below, Please select {self.num_of_examples} of them that meets the following requirement:\n\n"
                "First, it is NOT an oracle exmaple, second, it is NOT full circuit, third, it Must be a .qasm file, NOT an .py file.\n"
                "return the index of the path directly, nothing else is needed\n"
            )

        for i in range(0,len(top_paths)):
            prompt+=str(i)+'.\n'+top_paths[i][0]


        paths_index = self.llm.generate(prompt, role="info", max_tokens=100)

        print(paths_index)
        #return keyword_str.strip()

    def work(self, question=''):
        ##
        """
        Full pipeline: extract keywords -> retrieve top files from RAG -> form example
        """
        # Step 1: Extract keywords
        #keyword_query = self.get_key_words(question)
        keyword_query = self.get_key_words_for_full_circuit(question)


        # Step 2: Search top-k relevant file paths
        top_paths = self.RAG.search(keyword_query+'.qasm'+'n3' , top_k=1)

        # Step 3: Read each file and summarize with LLM
        examples = []
        for i, (path, score) in enumerate(top_paths, 1):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except Exception as e:
                explanations.append(f"🔸 File {i} ({path}) could not be read: {e}")
                continue

            one_example=f"File: {path}\n"+f"---\n{file_content[:1000]}\n---"
            examples.append(one_example)


        return examples    # actually it should be called 'possible info'

# === Test Code ===
if __name__ == "__main__":
    pass
