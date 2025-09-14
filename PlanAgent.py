import os
import json
import re
from typing import Dict, List, Tuple, Optional
import traceback

from LLM import LLM_model
from tools import RAG
from ToolsAgent import Tools_Agent
from GuidedAgent import Guided_Agent
from CalibrateAgent import Calibrate_Agent


# ---------- utils ----------
def _safe_read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def remove_json_comments(json_string: str) -> str:
    regex_pattern = r"\s*//.*"
    clean_lines = [re.sub(regex_pattern, "", line) for line in json_string.splitlines()]
    return "\n".join(clean_lines)

class Plan_Agent:

    def __init__(
        self,
        llm,
        rag,
        strategy= None,
    ):
        self.llm = llm
        self.rag = rag
        # default strategy
        self.strategy = strategy or {
            "guided":  ["bv", "dj", "grover", "qrng", "ghz", "cluster", "w_state", "qft", "or"],
            "tools":   ["adder", "pe", "permutation"]
        }

    def decompose(self, question):

        system_prompt = """
You are an expert AI assistant for quantum computing workflows. Your task is to analyze a user's request and decompose it into a structured computational graph.

Strict output requirements:
- Output MUST be a single valid JSON object (no commentary).
- Keys required:
  - "calibration": a string describing calibration tasks if any (e.g., "calibrate qubit-8 with new frequency 5.66e9"), or "No calibration needed."
  - "nodes": list of node objects:
      - id: unique string identifier (e.g., "grover_0")
      - name: algorithm name (e.g.,"bv", "grover", "dj", "adder", "pe", "permutation", "qrng", "qft", "w_state", "ghz", "cluster", "or")
      - logical_parameter: the minimal number of logical qubits in core logic (used for actual execution)
      - resource_parameter: the total qubit usage of the algorithm (reported at the end)
  - "edges": list of edge objects:
      - source: source node id
      - target: target node id
      - description: short explanation of what is being passed (e.g., "Use the output bitstring from qrng as inputs of adder.")

Rules:
- Encoding or mapping layers (e.g., amplitude encoding, direct state transfer) belong in edges, NOT nodes.
- Prefer the MINIMUM necessary logical_parameter.
- resource_parameter should reflect the total qubit footprint (ancillas etc.) if known; otherwise set it equal to logical_parameter.

Example 1 (Grover only)
User Request: "give me a circuit that performs grover's algorithm when qubit number = 3"
Your Output:
{
  "calibration": "No calibration needed.",
  "nodes": [
    {"id": "grover_0", "name": "grover", "logical_parameter": 3, "resource_parameter": 3}
  ],
  "edges": []
}

Example 2 (QRNG -> Adder)
User Request: "I need a qrng circuit that generates 4 random bits, then add the first 2 bits with the last 2 bits."
Your Output:
{
  "calibration": "No calibration needed.",
  "nodes": [
    {"id": "qrng_0", "name": "qrng", "logical_parameter": 4, "resource_parameter": 4},
    {"id": "adder_1", "name": "adder", "logical_parameter": 2, "resource_parameter": 6}
  ],
  "edges": [
    {"source": "qrng_0", "target": "adder_1",
     "description": "Split the 4 measured bits into two 2-bit integers and feed them to the adder."}
  ]
}

Example 3 (Calibration + DJ)
User Request: "I want to calibrate qubit-8 with new frequency 5.66e9. then I need a circuit for dj algorithm when qubit=6"
Your Output:
{
  "calibration": "calibrate qubit-8 with new frequency 5.66e9",
  "nodes": [
    {"id": "dj_0", "name": "dj", "logical_parameter": 6, "resource_parameter": 6}
  ],
  "edges": []
}
"""
        user_prompt = f'User Request: "{question}"\n'
        raw = self.llm.generate(user_prompt, system_prompt, max_tokens=10240)
        raw = remove_json_comments(raw)
        #print(raw)

        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end]) if start != -1 and end > 0 else {"calibration": "No calibration needed.", "nodes": [], "edges": []}
        except Exception as e:
            #print('error:',traceback.format_exc())
            return {"calibration": "No calibration needed.", "nodes": [], "edges": []}

    def _collect_related_schemas(self, graph):
        algos = sorted({(n.get("name") or "").strip().lower() for n in graph.get("nodes", []) if n.get("name")})
        blocks = []
        for algo in algos:
            p = os.path.join(".", "kernels", algo, f"{algo}_schema.txt")
            txt = _safe_read(p)
            if txt:
                blocks.append(f"### {algo} schema\n{txt.strip()}\n")
        return "\n".join(blocks).strip()

    def enrich(self, graph, original_question):
        if not graph or not graph.get("nodes"):
            return graph
        schema_appendix = self._collect_related_schemas(graph)
        system_prompt = f"""
You are a world-class expert in quantum computing implementation and resource estimation.
Enrich the following computational graph.

Do:
1) For each node, ensure the chosen parameters are MINIMAL and reasonable.
2) Add "parameter_reason" to each node, concisely explaining the chosen logical/resource parameters.
3) Remove any non-qubit-related parameters if present (keep only logical/resource parameters).
4) For each edge, refine "description" and explicitly mention transfer/encoding (e.g., "direct state transfer", "amplitude encoding", "parameter passing", or others).
5) For each edge, add "in_qubit_number" and "out_qubit_number" (strings are fine).
6) Normalize algorithm names to standard ones if needed.

You MUST return only a valid JSON object (no commentary).

Example Input:
{{
  "calibration": "No calibration needed.",
  "nodes": [
    {{"id":"qrng_0","name":"qrng","logical_parameter":4,"resource_parameter":4}},
    {{"id":"or_1","name":"or","logical_parameter":1,"resource_parameter":1}}
  ],
  "edges": [
    {{"source":"qrng_0","target":"or_1","description":"Use the measured results from qrng as the input state for or."}}
  ]
}}

Example Output:
{{
  "calibration": "No calibration needed.",
  "nodes": [
    {{
      "id":"qrng_0","name":"qrng","logical_parameter":4,"resource_parameter":4,
      "parameter_reason":"Generating 4 random bits simultaneously requires 4 qubits."
    }},
    {{
      "id":"or_1","name":"or","logical_parameter":5,"resource_parameter":5,
      "parameter_reason":"The OR gate consumes 4 logical input bits and uses 1 output bit."
    }}
  ],
  "edges": [
    {{
      "source":"qrng_0","target":"or_1",
      "in_qubit_number":"4","out_qubit_number":"5",
      "description":"parameter passing of 4 classical bits from QRNG to OR; no quantum remapping required."
    }}
  ]
}}

# Algorithm schemas appendix (for guidance):
{schema_appendix if schema_appendix else "[No schemas found for the referenced algorithms]"}
"""
        payload = json.dumps(graph, indent=2)
        user_prompt = f"The user question was: {original_question}\n\n{payload}"
        enriched = self.llm.generate(user_prompt, system_prompt, max_tokens=4096)
        enriched = remove_json_comments(enriched)
        try:
            return json.loads(enriched)
        except Exception:
            return graph

    def build_dispatch_plan(self, enriched_graph):
        plan = {}
        guided_set = set(a.lower() for a in self.strategy.get("guided", []))
        tools_set  = set(a.lower() for a in self.strategy.get("tools", []))

        for n in enriched_graph.get("nodes", []):
            algo = (n.get("name") or "").strip().lower()
            node_id = n.get("id")
            if not node_id:
                continue
            if algo in tools_set:
                route = "tools"
            elif algo in guided_set:
                route = "guided"
            else:
                route = "guided"
            plan[node_id] = {"algo": algo, "route": route}
        return plan


