from openai import OpenAI
import requests
from huggingface_hub import InferenceClient
class LLM_model:
    def __init__(self, llm_choice='gpt-4o', llm_key='',temp=None,provider='nebius'):
        """
        Initialize the LLM model.
        Supports OpenAI API ('gpt4o', 'gpt-4', 'gpt-3.5-turbo') and Hugging Face models with OpenAI-compatible chat interface.
        """
        self.llm_choice = llm_choice
        self.llm_key = llm_key
        self.use_openai = llm_choice in ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo']
        self.temp=temp
        if provider=='nscale':
            print('using provider NSCALE')
            self.client=OpenAI(
                base_url="https://inference.api.nscale.com/v1",
                api_key=self.llm_key,
                )

        elif provider=='huggingface':
            print('using provider HuggingFace')
            self.client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=self.llm_key,
            )   
        else:
            print('using provider NEBIUS')
            self.client = OpenAI(
                #base_url="https://inference.api.nscale.com/v1",
                base_url="https://api.studio.nebius.com/v1/",
                api_key=self.llm_key,
            )



        # Define system-level role prompts
        self.roles = {
            'raw_code': "generate code direcly, nothing else is needed",

            'n':'extract what is the qubit number n mentioned in the question. return the number directly, nothing else is needed.',


            'prompt': "You are an expert in AI-driven pedagogy. Generate a chain of thought prompt "
                      "that effectively explains the examples for the purpose of constructing guidance.",

            'info': "You are an expert in infomation extraction."
                      "You can effectlively process infomation or text based on user's instructions",


            'testcase': "You are a quantum software engineer specializing in test automation. Generate efficient "
                        "test cases that rigorously verify the correctness of the given problem implementation."
                        "return the code directly, no explanations or introductions, just the code without any other content.",

            'circuit': "You are a quantum computing expert. Generate a well-structured quantum circuit using\n"
                       "QASM 3.0 that correctly implements the given problem statement.\n"
                       "Please write OpenQASM 3.0 code following the syntax used in examples."
                        "Please write OpenQASM 3.0 code without using any kind of loop syntax. "
                        "This includes 'for', 'repeat', or any index-based iteration. "
                       "All repeated gate applications must be fully unrolled and written explicitly. "
                        "For example, instead of using a loop to apply 'h q[i]' to multiple qubits, "
                       "write each line separately: 'h q[0]; h q[1]; h q[2];' and so on. "
                        "return the code directly, no explanations or introductions, just the code without any other content.",

            'oracle': "You are a quantum information scientist. Generate an oracle function using QASM or Qiskit "
                      "that correctly represents the black-box quantum function for the given question."
                      "return the code directly, no explanations or introductions, just the code without any other content.",

            'reflection': "You are an AI debugging assistant in quantum computing (qasm and Qiskit, as well as python). Analyze the traceback error given in the prompt "
                          "and provide critical insights and specific modifications that another LLM can use to "
                          "improve the faulty code."
        }

    def generate(self, prompt, role='prompt', max_tokens=200):
        """
        Generates text using the chosen LLM API, based on the given role.
        """
        if role not in self.roles:
            raise ValueError(f"Invalid role: {role}. Choose from {list(self.roles.keys())}")

        system_prompt = self.roles[role]


        # configure model-specified prompts here
        if self.use_openai:
            return self._generate_openai(prompt, system_prompt, max_tokens)
        else:
            if 'deepseek' in self.llm_choice:
                prompt=prompt+'\nAVOID ANY CHINESE CHARACTERS! USE ENGLISH!'
                return self._generate_huggingface_chat(prompt, system_prompt, max_tokens)

            elif self.llm_choice=='Qwen/Qwen2.5-Coder-7B-Instruct':
                prompt=prompt+'start the code with "OPENQASM 3.0;" for the first line'

                return self._generate_huggingface_chat(prompt, system_prompt, max_tokens)
            else:
                return self._generate_huggingface_chat(prompt, system_prompt, max_tokens)

    def _generate_openai(self, prompt, system_prompt, max_tokens=200):
        headers = {"Authorization": f"Bearer {self.llm_key}"}

        if self.temp==None:
            data = {
                "model": self.llm_choice,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens
            }
        else:
            data = {
                "model": self.llm_choice,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature":self.temp,
            }            
        response = requests.post(self.api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"Error: {response.status_code}, {response.text}"

    def _generate_huggingface_chat(self, prompt, system_prompt, max_tokens=200):
        try:
            if self.temp==None:
                response = self.client.chat.completions.create(
                    model=self.llm_choice,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.llm_choice,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=self.temp
                )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during HuggingFace chat call: {str(e)}"


# Example Usage
if __name__ == "__main__":
    pass
