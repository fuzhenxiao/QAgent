from tools import *
from LLM import LLM_model
import traceback
import importlib.util
import os
import random
import json
import re
from Calibrator import Calibrator

def batch_calibrate(json_str, filename="./backend_27q.inc"):

    try:
        updates = json.loads(json_str)   
    except json.JSONDecodeError as e:
       print(f"illegal JSON: {e}")

    if not isinstance(updates, list):
        print("not a list")

    for entry in updates:
        name = entry.get("variable_name")
        value = entry.get("value")
        if name is None or value is None:
            print(f"invalid entry: {entry}")
            continue
        calibrate(name, value, filename=filename)  



class Calibrate_Agent(object):
    def __init__(self, llm_choice='', llm_key='',max_trial=3,show=False):
        self.max_trial=max_trial
        self.show=show
        self.LLM = LLM_model(llm_choice, llm_key, temp=1)
        self.calibrator = Calibrator(self.LLM)

    def _normalize_qubit_id(self, qubit_id):
        if isinstance(qubit_id, int):
            return qubit_id
        if isinstance(qubit_id, str):
            m = re.search(r"(\d+)", qubit_id)
            if m:
                return int(m.group(1))
        raise ValueError(f"Invalid qubit id: {qubit_id}")

    def _read_backend_text(self, filename="./backend_27q.inc"):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_const_float_map(self, filename="./backend_27q.inc"):
        text = self._read_backend_text(filename)
        pattern = r"const\s+float\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([0-9.+\-eE]+)\s*;"
        matches = re.findall(pattern, text)
        return {name: float(value) for name, value in matches}

    def _extract_resolver_mapping(self, resolver_name, filename="./backend_27q.inc"):
        text = self._read_backend_text(filename)
        pattern = rf"defcal\s+{re.escape(resolver_name)}\s+\$(\d+)\s+->\s+frame\s+f\s*\{{\s*f\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*;\s*\}}"
        pairs = re.findall(pattern, text)
        return {int(qid): target for qid, target in pairs}

    def load_backend_constraints(self, filename="./backend_27q.inc"):
        consts = self._extract_const_float_map(filename)
        drive_map = self._extract_resolver_mapping("_resolve_drive_frame", filename)
        readout_map = self._extract_resolver_mapping("_resolve_ro_frame", filename)

        qubits = {}
        qfreq_pattern = re.compile(r"^q(\d+)_freq$")
        rofreq_pattern = re.compile(r"^ro(\d+)_freq$")

        for name, value in consts.items():
            q_match = qfreq_pattern.match(name)
            ro_match = rofreq_pattern.match(name)
            if q_match:
                qid = int(q_match.group(1))
                qubits.setdefault(qid, {"qubit_id": qid})
                qubits[qid]["frequency"] = value
            elif ro_match:
                qid = int(ro_match.group(1))
                qubits.setdefault(qid, {"qubit_id": qid})
                qubits[qid]["readout_frequency"] = value

        for qid, port in drive_map.items():
            qubits.setdefault(qid, {"qubit_id": qid})
            qubits[qid]["drive_port"] = port

        for qid, port in readout_map.items():
            qubits.setdefault(qid, {"qubit_id": qid})
            qubits[qid]["readout_port"] = port

        return {
            "backend_file": filename,
            "qubit_count": len(qubits),
            "qubits": {f"q{qid}": qubits[qid] for qid in sorted(qubits)},
        }

    def get_qubit_profile(self, qubit_id, filename="./backend_27q.inc"):
        qid = self._normalize_qubit_id(qubit_id)
        constraints = self.load_backend_constraints(filename)
        key = f"q{qid}"
        if key not in constraints["qubits"]:
            raise ValueError(f"Qubit q{qid} not found in {filename}")
        return constraints["qubits"][key]

    def preview_frequency_update(self, qubit_id, new_freq, filename="./backend_27q.inc", readout=False):
        qid = self._normalize_qubit_id(qubit_id)
        profile = self.get_qubit_profile(qid, filename)
        field = "readout_frequency" if readout else "frequency"
        variable_name = f"ro{qid}_freq" if readout else f"q{qid}_freq"
        return {
            "qubit": f"q{qid}",
            "field": field,
            "variable_name": variable_name,
            "old_value": profile.get(field),
            "new_value": float(new_freq),
            "backend_file": filename,
        }

    def apply_frequency_update(self, qubit_id, new_freq, filename="./backend_27q.inc"):
        qid = self._normalize_qubit_id(qubit_id)
        preview = self.preview_frequency_update(qid, new_freq, filename, readout=False)
        calibrate(preview["variable_name"], float(new_freq), filename=filename)
        preview["applied"] = True
        return preview

    def apply_readout_update(self, qubit_id, new_freq, filename="./backend_27q.inc"):
        qid = self._normalize_qubit_id(qubit_id)
        preview = self.preview_frequency_update(qid, new_freq, filename, readout=True)
        calibrate(preview["variable_name"], float(new_freq), filename=filename)
        preview["applied"] = True
        return preview

    def estimate_drifted_frequency(self, qubit_id, drift, elapsed_hours, filename="./backend_27q.inc"):
        qid = self._normalize_qubit_id(qubit_id)
        profile = self.get_qubit_profile(qid, filename)
        base_freq = profile.get("frequency")
        if base_freq is None:
            raise ValueError(f"Base frequency for q{qid} not found in {filename}")
        return {
            "qubit": f"q{qid}",
            "base_frequency": base_freq,
            "drift_per_hour": float(drift),
            "elapsed_hours": float(elapsed_hours),
            "estimated_frequency": float(base_freq) + float(drift) * float(elapsed_hours),
        }

    def apply_drift_compensation(self, qubit_id, drift, elapsed_hours, filename="./backend_27q.inc"):
        estimate = self.estimate_drifted_frequency(qubit_id, drift, elapsed_hours, filename)
        applied = self.apply_frequency_update(qubit_id, estimate["estimated_frequency"], filename)
        estimate["applied_update"] = applied
        return estimate

    def batch_apply_calibration_plan(self, plan, filename="./backend_27q.inc", preview_only=False):
        if not isinstance(plan, list):
            raise ValueError("Calibration plan must be a list of update items")

        results = []
        for entry in plan:
            qid = entry.get("qubit")
            field = (entry.get("field") or "").strip().lower()
            value = entry.get("value")

            if qid is None or value is None:
                results.append({"success": False, "entry": entry, "reason": "Missing qubit or value"})
                continue

            try:
                if field in ("frequency", "drive_frequency", "qubit_frequency"):
                    if preview_only:
                        payload = self.preview_frequency_update(qid, value, filename, readout=False)
                    else:
                        payload = self.apply_frequency_update(qid, value, filename)
                elif field in ("readout_frequency", "ro_frequency"):
                    if preview_only:
                        payload = self.preview_frequency_update(qid, value, filename, readout=True)
                    else:
                        payload = self.apply_readout_update(qid, value, filename)
                else:
                    raise ValueError(f"Unsupported calibration field: {field}")

                payload["success"] = True
                results.append(payload)
            except Exception as e:
                results.append({"success": False, "entry": entry, "reason": str(e)})
        return results

    def generate_calibration_report(self, updates, filename="./backend_27q.inc"):
        if not isinstance(updates, list):
            updates = [updates]

        lines = [
            f"Calibration report for {filename}",
            f"Total updates: {len(updates)}",
        ]

        success_count = 0
        for item in updates:
            ok = bool(item.get("success", True))
            if ok:
                success_count += 1

            qubit = item.get("qubit", "unknown")
            field = item.get("field", item.get("variable_name", "unknown"))
            old_value = item.get("old_value", "N/A")
            new_value = item.get("new_value", item.get("estimated_frequency", "N/A"))
            reason = item.get("reason", "")
            status = "SUCCESS" if ok else "FAILED"

            line = f"- [{status}] {qubit} {field}: {old_value} -> {new_value}"
            if reason:
                line += f" ({reason})"
            lines.append(line)

        lines.insert(1, f"Successful updates: {success_count}")
        return "\n".join(lines)


    def solve_standard(self, description): # the most standard usage
        
        trial_num=0
        finally_success=False
        record='Failed to calibrate'
        while trial_num<self.max_trial:
            try:
                standard_task_instruction=self.calibrator.generate_calibration_instructions(description)
                batch_calibrate(standard_task_instruction)
                
                record='successfully calibrated!'
                print(record)
                finally_success=True
                break
            except Exception as e:
                print(f'error: e')
                print(f'retry: trial_num')
            trial_num+=1



        return '', record, finally_success

 


if __name__ == "__main__":
    pass
