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
    def generate(self, prompt, system_prompt, max_tokens=200):
        

        if self.use_openai:
            return self._generate_openai(prompt, system_prompt, max_tokens)
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
    # Hugging Face Example with OpenAI-style chat call
    hf_llm = LLM_model(
        llm_choice='Qwen/Qwen2.5-32B-Instruct',
        llm_key='YOUR OWN API KEY'
    )

    result = hf_llm.generate(
        "Construct an oracle for 4-qubit Deutsch-Jozsa algorithm. return the code directly, no explanations or introductions, just the python code without any other content",
        role="oracle",
        max_tokens=450
    )

    print(result)
