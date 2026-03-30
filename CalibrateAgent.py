from tools import *
from LLM import LLM_model
import traceback
import importlib.util
import os
import random
import json
from pathlib import Path
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


def _format_defcal_float(value: float) -> str:
    text = f"{float(value):.1e}"
    mantissa, exponent = text.split("e")
    exp_num = int(exponent)
    return f"{mantissa}e{exp_num}"


def _load_constraint_file(constraint_file: str) -> dict:
    with Path(constraint_file).open("r", encoding="utf-8") as f:
        return json.load(f)


def _select_constraint_qubit(data: dict, logical_label: str | None = None) -> dict:
    qubits = data.get("qubits", [])
    if not qubits:
        raise ValueError("Constraint file does not contain any qubits.")

    if logical_label is None:
        return qubits[0]

    for qubit in qubits:
        if qubit.get("logical_label") == logical_label:
            return qubit

    raise ValueError(f"Qubit {logical_label} not found in constraint file.")


def _resolve_constraint_drift(data: dict, logical_label: str) -> float:
    return float(data.get("metadata", {}).get("drift_hz", {}).get(logical_label, 0.0))


def generate_defcal_from_constraint(constraint_file: str, logical_label: str | None = None) -> str:
    data = _load_constraint_file(constraint_file)
    qubit = _select_constraint_qubit(data, logical_label=logical_label)

    label = qubit["logical_label"]
    drive_port = qubit["drive_port"]
    base_freq = float(qubit["resonance_freq_hz"])
    drift = _resolve_constraint_drift(data, label)

    return "\n".join(
        [
            'defcalgrammar "openpulse";',
            "",
            "cal {",
            f"    float base_freq_{label} = {_format_defcal_float(base_freq)};",
            f"    float delta_{label} = {_format_defcal_float(drift)};",
            "    // drift added here",
            f"    float calibrated_freq_{label} =",
            f"        base_freq_{label} + delta_{label};",
            "",
            f"    extern port {drive_port};",
            f"    frame fr_{label} = newframe({drive_port},",
            f"        calibrated_freq_{label}, 0.0);",
            "}",
        ]
    )


def write_defcal_from_constraint(
    constraint_file: str,
    output_file: str,
    logical_label: str | None = None,
) -> str:
    rendered = generate_defcal_from_constraint(constraint_file, logical_label=logical_label)
    Path(output_file).write_text(rendered + "\n", encoding="utf-8")
    return rendered



class Calibrate_Agent(object):
    def __init__(self, llm_choice='', llm_key='',max_trial=3,show=False):
        self.max_trial=max_trial
        self.show=show
        self.LLM = LLM_model(llm_choice, llm_key, temp=1)
        self.calibrator = Calibrator(self.LLM)


    def solve_standard(self, description):
        
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

    def solve_constraint_demo(self, constraint_file, logical_label=None, output_file=None):
        try:
            rendered = generate_defcal_from_constraint(
                constraint_file,
                logical_label=logical_label,
            )
            if output_file:
                Path(output_file).write_text(rendered + "\n", encoding="utf-8")
                record = f"generated defcal snippet from {constraint_file} and wrote it to {output_file}"
            else:
                record = f"generated defcal snippet from {constraint_file}"

            return rendered, record, True
        except Exception as e:
            return "", f"Failed to generate defcal from constraint file: {e}", False

 


if __name__ == "__main__":
    pass
