from tools import calibrate
from LLM import LLM_model
from Calibrator import Calibrator

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Union


Number = Union[int, float]


def _normalize_qubit_id(qubit_id: Union[str, int]) -> int:
    if isinstance(qubit_id, int):
        return qubit_id
    text = str(qubit_id).strip().lower()
    match = re.search(r"(\d+)", text)
    if not match:
        raise ValueError(f"Invalid qubit id: {qubit_id}")
    return int(match.group(1))


def _read_text(filename: str) -> str:
    return Path(filename).read_text(encoding="utf-8")


def _parse_float_constant(text: str, name: str) -> Optional[float]:
    pattern = rf"const\s+float\s+{re.escape(name)}\s*=\s*([0-9.+\-eE]+)\s*;"
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def _replace_float_constant_preview(text: str, name: str, new_value: Number) -> str:
    pattern = rf"(const\s+float\s+{re.escape(name)}\s*=\s*)([0-9.+\-eE]+)(\s*;)"
    repl = rf"\g<1>{float(new_value):.3f}\3"
    updated, count = re.subn(pattern, repl, text)
    if count == 0:
        raise ValueError(f"Parameter {name} not found in backend file")
    return updated


class Calibrate_Agent_Updated(object):
    def __init__(self, llm_choice: str = "", llm_key: str = "", max_trial: int = 3, show: bool = False):
        self.max_trial = max_trial
        self.show = show
        self.LLM = LLM_model(llm_choice, llm_key, temp=1)
        self.calibrator = Calibrator(self.LLM)

    def solve_standard(self, description: str, filename: str = "./backend_27q.inc"):
        trial_num = 0
        finally_success = False
        record = "Failed to calibrate"
        while trial_num < self.max_trial:
            try:
                standard_task_instruction = self.calibrator.generate_calibration_instructions(description)
                self.batch_apply_calibration(standard_task_instruction, filename=filename)
                record = "successfully calibrated!"
                finally_success = True
                break
            except Exception:
                pass
            trial_num += 1

        return "", record, finally_success

    def load_backend_constraints(self, filename: str = "./backend_27q.inc") -> Dict[str, object]:
        text = _read_text(filename)
        qubit_freqs = {
            int(idx): float(value)
            for idx, value in re.findall(r"const\s+float\s+q(\d+)_freq\s*=\s*([0-9.+\-eE]+)\s*;", text)
        }
        readout_freqs = {
            int(idx): float(value)
            for idx, value in re.findall(r"const\s+float\s+ro(\d+)_freq\s*=\s*([0-9.+\-eE]+)\s*;", text)
        }
        extern_ports = sorted(int(idx) for idx in re.findall(r"extern\s+port\s+q(\d+)\s*;", text))
        drive_frames = sorted(int(idx) for idx in re.findall(r"frame\s+q(\d+)_frame\s*=\s*newframe\(q\d+,\s*q\d+_freq,\s*0\);", text))

        qubits = {}
        all_ids = sorted(set(qubit_freqs) | set(readout_freqs) | set(extern_ports) | set(drive_frames))
        for qid in all_ids:
            qubits[qid] = {
                "qubit_id": qid,
                "drive_frequency": qubit_freqs.get(qid),
                "readout_frequency": readout_freqs.get(qid),
                "drive_port": f"d{qid}",
                "readout_port": f"r{qid}",
                "extern_port_declared": qid in extern_ports,
                "frame_declared": qid in drive_frames,
            }

        return {
            "backend_file": filename,
            "qubit_count": len(qubits),
            "qubits": qubits,
        }

    def get_qubit_profile(self, qubit_id: Union[str, int], filename: str = "./backend_27q.inc") -> Dict[str, object]:
        qid = _normalize_qubit_id(qubit_id)
        constraints = self.load_backend_constraints(filename=filename)
        if qid not in constraints["qubits"]:
            raise ValueError(f"Qubit q{qid} not found in {filename}")
        return constraints["qubits"][qid]

    def apply_frequency_update(self, qubit_id: Union[str, int], new_freq: Number, filename: str = "./backend_27q.inc") -> Dict[str, object]:
        qid = _normalize_qubit_id(qubit_id)
        before = self.get_qubit_profile(qid, filename=filename)
        calibrate(f"q{qid}_freq", float(new_freq), filename=filename)
        after = self.get_qubit_profile(qid, filename=filename)
        return {
            "qubit": f"q{qid}",
            "field": "drive_frequency",
            "old_value": before["drive_frequency"],
            "new_value": after["drive_frequency"],
            "success": True,
        }

    def apply_readout_update(self, qubit_id: Union[str, int], new_freq: Number, filename: str = "./backend_27q.inc") -> Dict[str, object]:
        qid = _normalize_qubit_id(qubit_id)
        before = self.get_qubit_profile(qid, filename=filename)
        calibrate(f"ro{qid}_freq", float(new_freq), filename=filename)
        after = self.get_qubit_profile(qid, filename=filename)
        return {
            "qubit": f"q{qid}",
            "field": "readout_frequency",
            "old_value": before["readout_frequency"],
            "new_value": after["readout_frequency"],
            "success": True,
        }

    def estimate_drifted_frequency(
        self,
        qubit_id: Union[str, int],
        drift_hz_per_hour: Number,
        elapsed_hours: Number = 1.0,
        base_frequency: Optional[Number] = None,
        filename: str = "./backend_27q.inc",
    ) -> Dict[str, object]:
        qid = _normalize_qubit_id(qubit_id)
        profile = self.get_qubit_profile(qid, filename=filename)
        base_freq = float(base_frequency) if base_frequency is not None else float(profile["drive_frequency"])
        drift = float(drift_hz_per_hour)
        hours = float(elapsed_hours)
        calibrated = base_freq + drift * hours
        return {
            "qubit": f"q{qid}",
            "base_frequency": base_freq,
            "drift_hz_per_hour": drift,
            "elapsed_hours": hours,
            "calibrated_frequency": calibrated,
        }

    def apply_drift_compensation(
        self,
        qubit_id: Union[str, int],
        drift_hz_per_hour: Number,
        elapsed_hours: Number = 1.0,
        filename: str = "./backend_27q.inc",
    ) -> Dict[str, object]:
        estimate = self.estimate_drifted_frequency(
            qubit_id=qubit_id,
            drift_hz_per_hour=drift_hz_per_hour,
            elapsed_hours=elapsed_hours,
            filename=filename,
        )
        update = self.apply_frequency_update(
            qubit_id=qubit_id,
            new_freq=estimate["calibrated_frequency"],
            filename=filename,
        )
        update["source"] = "drift_compensation"
        update["drift_hz_per_hour"] = estimate["drift_hz_per_hour"]
        update["elapsed_hours"] = estimate["elapsed_hours"]
        return update

    def preview_calibration(self, plan: List[Dict[str, object]], filename: str = "./backend_27q.inc") -> Dict[str, object]:
        original_text = _read_text(filename)
        preview_text = original_text
        changes = []

        for step in plan:
            qid = _normalize_qubit_id(step["qubit"])
            field = str(step["field"]).strip().lower()

            if field in ("frequency", "drive_frequency", "q_freq"):
                variable_name = f"q{qid}_freq"
            elif field in ("readout_frequency", "ro_frequency", "ro_freq"):
                variable_name = f"ro{qid}_freq"
            else:
                raise ValueError(f"Unsupported calibration field for preview: {field}")

            old_value = _parse_float_constant(preview_text, variable_name)
            new_value = float(step["value"])
            preview_text = _replace_float_constant_preview(preview_text, variable_name, new_value)
            changes.append(
                {
                    "qubit": f"q{qid}",
                    "field": field,
                    "variable_name": variable_name,
                    "old_value": old_value,
                    "new_value": new_value,
                }
            )

        return {
            "backend_file": filename,
            "changes": changes,
            "preview_text": preview_text,
        }

    def batch_apply_calibration(self, plan: Union[str, List[Dict[str, object]]], filename: str = "./backend_27q.inc") -> List[Dict[str, object]]:
        if isinstance(plan, str):
            parsed = json.loads(plan)
            if isinstance(parsed, list) and parsed and "variable_name" in parsed[0]:
                normalized_plan = []
                for entry in parsed:
                    variable_name = entry["variable_name"]
                    value = entry["value"]
                    if re.fullmatch(r"q\d+_freq", variable_name):
                        qid = int(re.search(r"\d+", variable_name).group(0))
                        normalized_plan.append({"qubit": qid, "field": "frequency", "value": value})
                    elif re.fullmatch(r"ro\d+_freq", variable_name):
                        qid = int(re.search(r"\d+", variable_name).group(0))
                        normalized_plan.append({"qubit": qid, "field": "readout_frequency", "value": value})
                    else:
                        raise ValueError(f"Unsupported calibration variable: {variable_name}")
                plan = normalized_plan
            else:
                plan = parsed

        results = []
        for step in plan:
            field = str(step["field"]).strip().lower()
            if field in ("frequency", "drive_frequency", "q_freq"):
                results.append(self.apply_frequency_update(step["qubit"], step["value"], filename=filename))
            elif field in ("readout_frequency", "ro_frequency", "ro_freq"):
                results.append(self.apply_readout_update(step["qubit"], step["value"], filename=filename))
            else:
                raise ValueError(f"Unsupported calibration field: {field}")
        return results

    def generate_calibration_report(
        self,
        plan: List[Dict[str, object]],
        filename: str = "./backend_27q.inc",
        applied_results: Optional[List[Dict[str, object]]] = None,
    ) -> Dict[str, object]:
        preview = self.preview_calibration(plan, filename=filename)
        if applied_results is None:
            applied_results = []

        return {
            "backend_file": filename,
            "success": True,
            "change_count": len(preview["changes"]),
            "changes": preview["changes"],
            "applied_results": applied_results,
            "summary": [
                f"{item['qubit']} {item['field']}: {item['old_value']} -> {item['new_value']}"
                for item in preview["changes"]
            ],
        }

    def generate_openpulse_stub(
        self,
        qubit_id: Union[str, int],
        drift_hz_per_hour: Number = 0.0,
        elapsed_hours: Number = 0.0,
        filename: str = "./backend_27q.inc",
    ) -> str:
        estimate = self.estimate_drifted_frequency(
            qubit_id=qubit_id,
            drift_hz_per_hour=drift_hz_per_hour,
            elapsed_hours=elapsed_hours,
            filename=filename,
        )
        qid = _normalize_qubit_id(qubit_id)
        calibrated = estimate["calibrated_frequency"]
        return (
            'defcalgrammar "openpulse";\n'
            "cal {\n"
            f"  float calibrated_freq_q{qid} = {calibrated:.3f};\n"
            f"  frame calibrated_q{qid}_frame = newframe(q{qid}, calibrated_freq_q{qid}, 0);\n"
            "}\n"
        )


if __name__ == "__main__":
    pass
