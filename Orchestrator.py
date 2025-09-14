# Orchestrator.py
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
from PlanAgent import Plan_Agent


class Orchestrator:
    def __init__(self, llm_choice,llm_key,strategy= None):
        self.llm = LLM_model(llm_choice, llm_key)
        self.rag = RAG(root_folder="./kernels")
        self.tools = Tools_Agent(llm_choice, llm_key)
        self.guided = Guided_Agent(llm_choice, llm_key)
        self.calibrator = Calibrate_Agent(llm_choice, llm_key)
        self.planner = Plan_Agent(self.llm, self.rag, strategy=strategy)

    @staticmethod
    def _call_solver(agent, algo, qubits):
        for name in ("solve_standard", "solve", "__call__"):
            m = getattr(agent, name, None)
            if callable(m):
                return m(algo=algo, qubit_num=qubits)
        print(f"Agent {agent.__class__.__name__} has no callable solver")

    @staticmethod
    def _is_qasm(text):
        if not isinstance(text, str):
            return False
        t = text.strip()
        return ("openqasm" in t.lower()) or ("qelib1.inc" in t)

    @staticmethod
    def _fmt_bool(b):
        return "Success" if b else "Failed"

    def _build_final_report(self,user_request,enriched_plan,results,resource_summary,calibration = None):
        node_success = all(v.get("success") for v in results.values()) if results else True
        calib_success = (calibration.get("success") if calibration else True)
        overall_success = bool(node_success and calib_success)


        node_lines = []
        for n in enriched_plan.get("nodes", []):
            nid = n.get("id"); algo = n.get("name")
            lp  = n.get("logical_parameter"); rp = n.get("resource_parameter", lp)
            reason = n.get("parameter_reason", "")
            node_lines.append(f"- **{nid}** ({algo}): logical={lp}, resource={rp}" + (f" — _{reason}_" if reason else ""))

        total_qubits = resource_summary.get("total_resource_qubits", 0)

        edge_lines = []
        for e in enriched_plan.get("edges", []):
            src = e.get("source"); tgt = e.get("target")
            desc = e.get("description", "")
            inq = e.get("in_qubit_number", "")
            outq = e.get("out_qubit_number", "")
            io = []
            if inq: io.append(f"in={inq}")
            if outq: io.append(f"out={outq}")
            io_str = (f" ({', '.join(io)})" if io else "")
            edge_lines.append(f"- {src} → {tgt}{io_str}: {desc}")

        qasm_blocks = []
        for n in enriched_plan.get("nodes", []):
            nid = n.get("id"); algo = n.get("name")
            r = results.get(nid, {})
            artifact = r.get("code", "")
            if self._is_qasm(artifact):
                qasm_blocks.append(f"### Node {nid} ({algo})\n```qasm\n{artifact.strip()}\n```")
            else:
                msg = r.get("report", "")
                qasm_blocks.append(
                    f"### Node {nid} ({algo})\n"
                    f"_No OpenQASM detected in artifact; showing raw output for debugging._\n\n"
                    f"```text\n{(artifact or '').strip()}\n```\n"
                    + (f"> Report note: {msg}\n" if msg else "")
                )

        calib_section = ""
        if calibration:
            cdesc = calibration.get("description", "")
            crep = calibration.get("report", "")
            calib_section = (
                "## Calibration\n"
                f"- Request: {cdesc}\n"
                f"- Status: {self._fmt_bool(calibration.get('success'))}\n"
                + (f"```text\n{crep.strip()}\n```\n" if crep else "")
            )


        report = [
            "# Quantum Workflow Report",
            f"**Overall Status:** {self._fmt_bool(overall_success)}",
            "",
            "## User Request",
            f"> " + user_request.replace("\n", "\n> "),
            "",
            calib_section if calib_section else "",
            "## Qubit Usage",
            *(node_lines or ["(no nodes)"]),
            f"\n**Total resource qubits:** {total_qubits}",
            "",
            "## Data Transfers (Edges)",
            *(edge_lines or ["(no edges)"]),
            "",
            "## QASM Artifacts",
            *(qasm_blocks or ["(no artifacts)"]),
        ]

        return "\n".join([line for line in report if line is not None])


    def run(self, user_request):


        print('generating plan')
        plan = self.planner.decompose(user_request)
        print('reviewing plan')
        enriched = self.planner.enrich(plan, user_request)
        print('assigning tasks')
        dispatch = self.planner.build_dispatch_plan(enriched)


        calib_desc = (plan.get("calibration") or "").strip()
        calib_payload = None
        if calib_desc and calib_desc.lower() != "no calibration needed.":
            _, calib_report, calib_ok = self.calibrator.solve_standard(calib_desc)

            calib_payload = {"description": calib_desc, "report": calib_report, "success": bool(calib_ok)}


        results = {}
        total_resource = 0
        for n in enriched.get("nodes", []):
            nid = n.get("id"); algo = (n.get("name") or "").strip().lower()
            lp  = int(n.get("logical_parameter", 0) or 0)
            rp  = int(n.get("resource_parameter", lp) or lp)
            total_resource += rp

            route = dispatch.get(nid, {}).get("route", "guided")
            agent = self.guided if route == "guided" else self.tools

            try:
                code, report, ok = self._call_solver(agent, algo=algo, qubits=lp)
            except Exception as e:
                code, report, ok = "", f"Execution error: {e}", False

            results[nid] = {
                "algo": algo, "route": route,
                "logical_parameter": lp, "resource_parameter": rp,
                "code": code, "report": report, "success": bool(ok)
            }

        payload = {
            "plan": plan,
            "enriched_plan": enriched,
            "dispatch_plan": dispatch,
            "calibration": calib_payload,
            "results": results,
            "resource_summary": {"total_resource_qubits": total_resource}
        }

        payload["final_report"] = self._build_final_report(
            user_request=user_request,
            enriched_plan=enriched,
            results=results,
            resource_summary=payload["resource_summary"],
            calibration=calib_payload
        )

        return payload


if __name__ == "__main__":
    pass
