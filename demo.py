# demo.py
import os
import json
from datetime import datetime

from Orchestrator import Orchestrator

#========LLM configs========

LLM_CHOICE = 'Qwen/Qwen3-Coder-30B-A3B-Instruct'
LLM_KEY = 'Your Own Key'
# by default the llm provider is Nebius.
# Nscale and openai are also available
# can be further extended in LLM.py 

#========assignment strategy========
#========    optional       ========
strategy = {
    "guided":  ["bv", "dj", "grover", "qrng", "ghz", "cluster", "qft", "or"],
    "tools":   ["adder", "pe", "permutation", "w_state","unknown"],   
    # any task that is not included in the database will be assigned to Tools-Augmented Coding Agent
}


# for now only "bv", "dj", "grover", "qrng", "ghz", "cluster", "qft", "or", "adder", "pe", "permutation", "w_state" are included in the knowledge base
# but it can be extended by offering examples or generation-tools

demo_request = (
    "Calibrate device: set qubit-8 frequency to 5.66e9, then Use QRNG to generate 10 random qubits, "
    "split into two 5-qubit registers, add them with the quantum adder to get a 5-bit number "
    "(abandon the cout), then apply permutation by 1 bit."
)

def main():

    orch = Orchestrator(LLM_CHOICE, LLM_KEY, strategy=strategy)
    payload = orch.run(demo_request)

    # prepare some files to store the final results
    os.makedirs("reports", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = os.path.join("reports", f"report_{ts}.md")
    json_path = os.path.join("reports", f"report_{ts}.json")

    # write human-readable report
    final_report = payload.get("final_report", "# Report\n(No report generated)")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_report)

    # write full payload for debugging/auditing
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Human-readable report written to: {md_path}")
    print(f"Full JSON payload written to: {json_path}")

if __name__ == "__main__":
    # for the first run, it will take ~1 minute for the RAG module to finish mapping.
    main()
