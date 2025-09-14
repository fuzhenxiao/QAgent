
from tools import *
import ast
import io
import os
import sys
import types
import traceback
import importlib.util
from contextlib import redirect_stdout
import threading
import time
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Execution time exceeded")


# The reviewer within Tools-Augmented Coding Agent
class T_Reviewer(object):
    def __init__(self, llm, max_history=10):
        self.llm = llm
        self.qasm_tester = None 
        self.max_history = max_history
        self.system_prompt = ''
        self.history = [] 


    def _load_kernel_tools(self, algo):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        rel_path = os.path.join(base_dir, "kernels", "kernel_tools", f"{algo}_tools.py")
        if not os.path.exists(rel_path):
            raise FileNotFoundError(f"Kernel tools not found at: {rel_path}")
        mod_name = f"_kernel_tools_{algo}"
        spec = importlib.util.spec_from_file_location(mod_name, rel_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load spec for: {rel_path}")
        module = importlib.util.module_from_spec(spec)
        module.__package__ = None
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        return module

    def _prepare_exec_env(self, tools_module):
        env = {
            "__name__": "__main__", 
            "__file__": getattr(tools_module, "__file__", None),
        }

        for k in dir(tools_module):
            if not k.startswith("_"):
                env[k] = getattr(tools_module, k)
        return env

    def _summarize_exception(self, err):
        etype = type(err).__name__
        tb = traceback.format_exc()

        if isinstance(err, SyntaxError):
            return (
                f"SyntaxError: {err.msg} at line {getattr(err, 'lineno', '?')}, "
                f"offset {getattr(err, 'offset', '?')}. "
                "Fix the syntax at the indicated location. Common issues: missing colons, unmatched parentheses, "
                "bad indentation, or stray characters."
            )
        if isinstance(err, NameError):
            return (
                f"NameError: {err}. You referenced a name that isn't defined in the script. "
                "Make sure you imported it from the kernel tools or defined it before use."
            )
        if isinstance(err, AttributeError):
            return (
                f"AttributeError: {err}. You likely used a function/attribute that doesn't exist. "
                "Check the available functions in the kernel tools and their signatures."
            )
        if isinstance(err, ImportError) or isinstance(err, ModuleNotFoundError):
            return (
                f"{etype}: {err}. Ensure the module path and package structure are correct "
                "(no file paths in imports; use dotted paths) and that required dependencies are installed."
            )
        if isinstance(err, TypeError):
            return (
                f"TypeError: {err}. You may be passing wrong argument types/counts. "
                "Verify the function signatures from the kernel tools."
            )
        if isinstance(err, ValueError):
            return (
                f"ValueError: {err}. Check the values and constraints you're passing into the functions "
                "(e.g., qubit indices within range, non-empty circuit, etc.)."
            )

        last_lines = "".join(tb.strip().splitlines()[-3:])
        return f"{etype}: {err}. Traceback (last lines): {last_lines}"

    def _trim_history(self):
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def generate_reflection(self, pythoncode, algo, qubit_num):
        try:
            tools_module = self._load_kernel_tools(algo)
        except Exception as e:
            reflection = self._summarize_exception(e)
            report = f"Failed to load kernel tools for '{algo}'."
            record = {
                "algo": algo,
                "qubit_num": qubit_num,
                "pythoncode": pythoncode,
                "success": False,
                "qasm": None,
                "report": report,
                "reflection": reflection,
                "stage": "load_kernel_tools",
            }
            self.history.append(record)
            self._trim_history()
            return False, reflection, report

        # 1) Syntax check
        try:
            ast.parse(pythoncode)
        except Exception as e:
            reflection = self._summarize_exception(e)
            report = "Syntax check failed."
            record = {
                "algo": algo,
                "qubit_num": qubit_num,
                "pythoncode": pythoncode,
                "success": False,
                "qasm": None,
                "report": report,
                "reflection": reflection,
                "stage": "syntax_check",
            }
            self.history.append(record)
            self._trim_history()
            return False, reflection, report

        # 2) Execute the code and capture stdout
        exec_env = self._prepare_exec_env(tools_module)
        stdout_buf = io.StringIO()
        timer=threading.Timer(60,timeout_handler)
        timer.start()
        try:
            with redirect_stdout(stdout_buf):
                exec(pythoncode, exec_env, exec_env)
        except Exception as e:
            reflection = self._summarize_exception(e)
            captured = stdout_buf.getvalue()
            # it is possible that nothing got printed
            captured_hint = f"Captured error:{e}, instead of implementing the tools, calling existing tools directly is recommended."
            if not captured.strip():
                captured_hint += " And there is no output captured from the script."
            report = f"Execution error. {captured_hint}"
            record = {
                "algo": algo,
                "qubit_num": qubit_num,
                "pythoncode": pythoncode,
                "success": False,
                "qasm": None,
                "report": report,
                "reflection": reflection,
                "stage": "execute",
            }
            self.history.append(record)
            self._trim_history()
            return False, reflection, report
        finally:
            timer.cancel()


        output = stdout_buf.getvalue().strip()

        # 3) Validate QASM output presence
        if not output:
            reflection = (
                "No QASM was printed. Ensure your script prints the final QASM to stdout, "
                "for example:\n\n"
                "    qasm = build_my_qasm(...)\n"
                "    print(qasm)\n\n"
                "Also verify that functions from the kernel tools return QASM or that you convert the circuit to QASM."
            )
            report = "Script ran without errors, but produced no output."
            record = {
                "algo": algo,
                "qubit_num": qubit_num,
                "pythoncode": pythoncode,
                "success": False,
                "qasm": None,
                "report": report,
                "reflection": reflection,
                "stage": "no_qasm_output",
            }
            self.history.append(record)
            self._trim_history()
            return False, reflection, report

        qasm_text = output

        looks_like_qasm = ("OPENQASM" in qasm_text) or ("qreg " in qasm_text) or ("creg " in qasm_text)
        if not looks_like_qasm:
            qasm_warning = (
                "Warning: Output does not resemble standard OpenQASM (missing 'OPENQASM', 'qreg', or 'creg'). "
                "If your tester expects OpenQASM, make sure you export/print in that format."
            )
        else:
            qasm_warning = None

        # 4) Test QASM
        if self.qasm_tester is None:
            reflection = (
                "QASM generated, but no qasm_tester is configured. "
                "Set `self.qasm_tester` to an object that implements `test(qasm, qubit_num)`."
            )
            report = "Tester missing; cannot validate QASM."
            record = {
                "algo": algo,
                "qubit_num": qubit_num,
                "pythoncode": pythoncode,
                "success": False,
                "qasm": qasm_text,
                "report": report,
                "reflection": reflection,
                "stage": "tester_missing",
            }
            self.history.append(record)
            self._trim_history()
            return False, reflection, report

        try:

            #print('!!!!!!\n',qasm_text)
            issuccess, successrate, reportdetail = self.qasm_tester.test(qasm_text, qubit_num)
        except Exception as e:
            reflection = (
                "QASM was produced, but the tester raised an error. "
                "Ensure the QASM matches the tester's expected dialect and qubit count. "
                + self._summarize_exception(e)
            )
            report = "Tester threw an exception."
            record = {
                "algo": algo,
                "qubit_num": qubit_num,
                "pythoncode": pythoncode,
                "success": False,
                "qasm": qasm_text,
                "report": report,
                "reflection": reflection,
                "stage": "tester_exception",
            }
            self.history.append(record)
            self._trim_history()
            return False, reflection, report

        # Construct final report string with optional warning
        full_report = f"success={issuccess}, success_rate={successrate}\n{reportdetail}"
        if qasm_warning:
            full_report = qasm_warning + "\n\n" + full_report

        if issuccess:
            record = {
                "algo": algo,
                "qubit_num": qubit_num,
                "pythoncode": pythoncode,
                "success": True,
                "qasm": qasm_text,
                "report": full_report,
                "reflection": "Verified",
                "stage": "verified",
            }
            self.history.append(record)
            self._trim_history()
            return True, qasm_text, full_report

        else:
            # Generate a reflection via LLM if available, otherwise fall back to a heuristic suggestion
            reflection_prompt = (
                "You are a reviewer. Given the algorithm name, the number of qubits, the user code, and the tester "
                "report, provide a short, actionable suggestion (reflection) to fix the code so it passes.\n\n"
                f"Algorithm: {algo}\n"
                f"Qubits: {qubit_num}\n"
                "User code:\n"
                "```\n" + pythoncode + "\n```\n\n"
                "Tester report:\n"
                + full_report
            )
            try:
                reflection = self.llm.generate(reflection_prompt, self.system_prompt, max_tokens=10240)
                if not isinstance(reflection, str) or not reflection.strip():
                    raise ValueError("Empty reflection from LLM.")
            except Exception:
                # Fallback heuristic reflection
                reflection = (
                    "Tester indicates failure. Verify that gates match the expected algorithm, "
                    "register sizes equal the provided qubit count, and measurement order matches the tester. "
                    "Print the final circuit as valid OpenQASM 2.0."
                )

            record = {
                "algo": algo,
                "qubit_num": qubit_num,
                "pythoncode": pythoncode,
                "success": False,
                "qasm": qasm_text,
                "report": full_report,
                "reflection": reflection,
                "stage": "tested_failed",
            }
            self.history.append(record)
            self._trim_history()
            return False, reflection, full_report

# === Test Code ===
if __name__ == "__main__":
    pass


