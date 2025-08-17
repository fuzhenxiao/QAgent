from LLM import LLM_model
import os
import glob
import re
import ast
import yaml
import importlib
import os
import random
import time
import os
import random
from LLM import LLM_model  
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
def clean_qasm_string(s):

    s = s.strip().strip("`")

    start_index = s.find("OPENQASM")
    if start_index != -1:
        return s[start_index:].strip()
    return s.strip()  

class Baseline:
    def __init__(self, llm, rag=None):
        self.llm = llm

    def infer_answer_filename(self, algo_name, qubit_num):
        if algo_name == "bv":
            return f"bernstein_vazirani_n{qubit_num}.qasm"
        elif algo_name == "dj":
            return f"deutsch_jozsa_n{qubit_num}.qasm"
        elif algo_name == "pe":
            return f"phase_estimation_n{qubit_num}.qasm"
        else:
            return f"{algo_name}_n{qubit_num}.qasm"

    def get_random_shots(self, algo_name, current_n, k=5):
        folder = os.path.join("answers", algo_name,'example')
        all_files = os.listdir(folder)
        candidates = [f for f in all_files if f.endswith(".qasm") and f != f'n{current_n}.qasm']

        # for pe, n should < 8 or the prompt would be too long
        if algo_name == "pe":
            def extract_n(fname):
                try:
                    return int(fname.split("n")[-1].split(".")[0])
                except:
                    return 999
            candidates = [f for f in candidates if extract_n(f) < 8]

        samples = random.sample(candidates, min(k, len(candidates)))

        print(f"[Sampling] For {algo_name}, n={current_n}, selected examples:")
        for s in samples:
            print(" -", os.path.join(folder, s))

        shots = []
        for fname in samples:
            try:
                n = int(fname.split("n")[-1].split(".")[0])
                with open(os.path.join(folder, fname), "r") as f:
                    code = f.read().strip()
                q_text = self.get_question(algo_name).replace("_NUM_", str(n))
                shots.append(f"one possible example code is:\n{code}")
            except Exception as e:
                print(f"Skipping {fname}: {e}")
        return "\n\n".join(shots)

    def get_question(self, algo_name):
        return self.questions[algo_name]

    def compute_bleu(self, ref, gen):
        ref_tokens = ref.split()
        gen_tokens = gen.split()
        return sentence_bleu([ref_tokens], gen_tokens, smoothing_function=SmoothingFunction().method1)

    def evaluate_bleu(self, output_folder):
        print("\n=== BLEU Evaluation ===")
        for algo_name in self.questions:
            generated_dir = os.path.join(output_folder, algo_name)
            answers_dir = os.path.join("answers", algo_name)
            if not os.path.exists(generated_dir):
                continue
            scores = []
            for fname in os.listdir(generated_dir):
                if not fname.endswith(".qasm"): continue
                try:
                    n = int(fname.split("n")[-1].split(".")[0])
                    ref_file = os.path.join(answers_dir, self.infer_answer_filename(algo_name, n))
                    gen_file = os.path.join(generated_dir, fname)
                    if not os.path.exists(ref_file): continue
                    with open(ref_file) as rf, open(gen_file) as gf:
                        ref = rf.read().strip()
                        gen = gf.read().strip()
                    bleu = self.compute_bleu(ref, gen)
                    scores.append(bleu)
                except Exception as e:
                    print(f"BLEU skip {fname}: {e}")
            if scores:
                avg = sum(scores) / len(scores)
                print(f"{algo_name.upper():<15} Average BLEU: {avg:.3f}")
            else:
                print(f"{algo_name.upper():<15} No valid outputs to score.")

    def generate_all(self, qubit_list, output_folder="reports_baseline_llama"):
        os.makedirs(output_folder, exist_ok=True)
        for algo_name in self.questions:
            algo_folder = os.path.join(output_folder, algo_name)
            os.makedirs(algo_folder, exist_ok=True)
            for n in qubit_list:
                #time.sleep(5)
                target_question = self.get_question(algo_name).replace("_NUM_", str(n))
                few_shots = self.get_random_shots(algo_name, n, k=5)
                prompt = f"{few_shots}\n\nNow, answer this question: {target_question}, please mind that do not add comments or explanations, just output the code itself, nothing else! don't forget to include oracle.inc, it is necessary"
                answer = self.llm.generate(prompt, "examples:", 1000)
                answer=clean_qasm_string(answer)
                print(answer)

                output_path = os.path.join(algo_folder, f"n{n}.qasm")
                with open(output_path, "w") as f:
                    f.write(answer)

        self.evaluate_bleu(output_folder)

    def set_question_bank(self, question_dict):
        self.questions = question_dict
