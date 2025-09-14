from tools import load_function_from_script
from LLM import LLM_model
from T_Advisor import T_Advisor          
from T_Coder import T_Coder       
from T_Reviewer import T_Reviewer      

import os
import time


class _UniversalCheckWrapper:
    def __init__(self, check_fn):
        self._check = check_fn

    def test(self, qasm, qubit_num):
        return self._check(qasm, qubit_num)

class Tools_Agent(object):

    def __init__(self, llm_choice = '', llm_key = '', reflection_round = 3,temp=None, candidate_num= 3, show = False):
        self.reflection_round = max(0, int(reflection_round))
        self.candidate_num = max(1, int(candidate_num))
        self.show = show

        self.LLM = LLM_model(llm_choice, llm_key, temp=temp)
        self.advisor = T_Advisor(self.LLM)   
        self.coder = T_Coder(self.LLM)      
        self.reviewer = T_Reviewer(self.LLM) 

    def _load_qasm_tester(self, algo):
        test_script_path = f'./kernels/{algo}/universal_test.py'
        check_fn = load_function_from_script(test_script_path, 'universal_check') 
        return _UniversalCheckWrapper(check_fn)

    def _make_record_line(self, cand_idx, trial_idx, success, reason):
        stat = "success" if success else "failed"
        return f"candidate #{cand_idx}, trial #{trial_idx}, {stat}, reason is {reason}"

    def snapshot_usage(self):
        self.LLM.snapshot_usage()

    def usage_since_snapshot(self):
        return self.LLM.usage_since_snapshot()

    def solve_standard(self, algo, qubit_num, shots=3):

        if self.show:
            print(f'[ToolsAgent] solving {algo} when q = {qubit_num}')

        record = []
        final_code = None
        finally_success = False

        qasm_tester = self._load_qasm_tester(algo)
        self.reviewer.history = []
        self.reviewer.qasm_tester = qasm_tester  

        if self.show:
            print(f'tester loaded for {algo}')

        try:
            if self.show:
                print(f'loading tools description')
            tools_description, plan, _ = self.advisor.conclude_coding_info(algo=algo)
            if self.show:
                print(f'description loaded')
        except Exception as e:
            if self.show:
                print('advisor error:', e)
            record.append(self._make_record_line(0, 0, False, f"advisor failed: {e}"))
            tools_description, plan = "", ""

        if self.show:
            print(f'plan/tools extracted for {algo} q = {qubit_num}')

        # Generate candidates
        candidates = []
        for i in range(self.candidate_num):
            try:
                code = self.coder.generate_code(tools_description, plan, algo, qubit_num)
                candidates.append(code)
            except Exception as e:
                if self.show:
                    print('codegen error:', e)
                record.append(self._make_record_line(i + 1, 1, False, f"generation error: {e}"))
                candidates.append("")

        if self.show:
            print(f'{len(candidates)} candidates generated.')

        # Reflection loop
        for ci, code in enumerate(candidates, start=1):
            self.reviewer.history = []
            current_code = code
            #if self.show:
                #print(f'current code is\n{current_code}')
            for ti in range(1, self.reflection_round + 1):
                if self.show:
                    print(f'candidate {ci}, reflection round {ti} — testing...')
                try:
                    # T_Reviewer requires (pythoncode, algo, qubit_num)
                    success, message_or_reflection, report = self.reviewer.generate_reflection(
                        current_code, algo=algo, qubit_num=qubit_num
                    )

                    if self.show:
                        #print(current_code,'\n')
                        print(f'test result is {report}')
                except Exception as e:
                    if self.show:
                        print('reviewer crashed:', e)
                    record.append(self._make_record_line(ci, ti, False, f"reviewer crashed: {e}"))
                    continue

                if success:
                    qasm_text = message_or_reflection
                    record.append(self._make_record_line(ci, ti, True, "passed all tests"))
                    final_code = current_code
                    finally_success = True
                    if self.show:
                        print('success!')
                    return qasm_text, record, finally_success

                # Failed — use reflection to regenerate
                record.append(self._make_record_line(ci, ti, False, report))
                try:
                    current_code = self.coder.regenerate_code(
                        algo=algo,
                        qubit_num=qubit_num,
                        code=current_code,
                        error=report,
                        suggestion=message_or_reflection
                    )
                except Exception as e:
                    if self.show:
                        print('regenerate error:', e)
                    record.append(self._make_record_line(ci, ti + 1, False, f"regeneration error: {e}"))
                    continue

        # Exhausted
        final_code = current_code if current_code else None
        if self.show:
            print('failed!')
        return final_code, record, finally_success

    def solve_without_reflection(self, algo, qubit_num, shots=3):
        record = []

        qasm_tester = self._load_qasm_tester(algo)
        self.reviewer.history = []
        self.reviewer.qasm_tester = qasm_tester

        # Advisor
        try:
            tools_description, plan, _ = self.advisor.conclude_coding_info(algo=algo)
        except Exception as e:
            record.append(self._make_record_line(1, 1, False, f"advisor failed: {e}"))
            tools_description, plan = "", ""

        try:
            code = self.coder.generate_code(tools_description, plan, algo, qubit_num)
        except Exception as e:
            record.append(self._make_record_line(1, 1, False, f"generation error: {e}"))
            return None, record, False


        ok, _, report = self.reviewer.generate_reflection(code, algo=algo, qubit_num=qubit_num)
        if ok:
            record.append(self._make_record_line(1, 1, True, "passed all tests"))
            return message_or_reflection, record, True
        else:
            record.append(self._make_record_line(1, 1, False, report))
            return code, record, False

    def solve_without_plan(self, algo, qubit_num= 5, shots= 3, show = False):

        if self.show:
            print(f'[ToolsAgent] solving (no plan) {algo} when q = {qubit_num}')

        record = []
        final_code = None
        finally_success = False

        qasm_tester = self._load_qasm_tester(algo)
        self.reviewer.history = []
        self.reviewer.qasm_tester = qasm_tester

        # Advisor
        try:
            tools_description, plan, _ = self.advisor.conclude_coding_info(algo=algo)
            plan = 'NO AVAILABLE PLAN'
        except Exception as e:
            if self.show:
                print('advisor error:', e)
            record.append(self._make_record_line(0, 0, False, f"advisor failed: {e}"))
            tools_description, plan = "", ""

        # Generate candidates
        candidates = []
        for i in range(self.candidate_num):
            try:
                candidates.append(self.coder.generate_code(tools_description, plan, algo, qubit_num))
            except Exception as e:
                if self.show:
                    print('codegen error:', e)
                record.append(self._make_record_line(i + 1, 1, False, f"generation error: {e}"))
                candidates.append("")

        # Reflection loop
        for ci, code in enumerate(candidates, start=1):
            self.reviewer.history = []
            current_code = code
            if self.show:
                print(f'current code is\n{current_code}')
            for ti in range(1, self.reflection_round + 1):
                try:
                    ok, reflection, report = self.reviewer.generate_reflection(current_code, algo=algo, qubit_num=qubit_num)
                    if self.show:
                        print(f'test result is {report}')
                except Exception as e:
                    record.append(self._make_record_line(ci, ti, False, f"reviewer crashed: {e}"))
                    continue

                if ok:
                    record.append(self._make_record_line(ci, ti, True, "passed all tests"))
                    final_code = current_code
                    finally_success = True
                    return final_code, record, finally_success

                record.append(self._make_record_line(ci, ti, False, report))
                try:
                    current_code = self.coder.regenerate_code(
                        algo=algo,
                        qubit_num=qubit_num,
                        code=current_code,
                        error=report,
                        suggestion=reflection
                    )
                except Exception as e:
                    record.append(self._make_record_line(ci, ti + 1, False, f"regeneration error: {e}"))
                    continue

        final_code = candidates[-1] if candidates else None
        return final_code, record, finally_success


# =============================for testing only========================
def run_tests(algos, qubitrange, avg=3, logfile='./log_tools.txt', logfiledetail='./log_tools_detail.txt',
              llm_choice='', llm_key=''):
    def classify_error(err_msg: str) -> str:

        if not err_msg:
            return "unknown"

        m = err_msg.strip().lower()

        if "passed all tests" in m:
            return "success"
        if "invalid syntax" in m or "syntaxerror" in m:
            return "python_syntax"
        if "nameerror" in m or "attributeerror" in m or "typeerror" in m or "runtimeerror" in m:
            return "python_runtime"
        if "qasm parsing failed" in m or "invalid qasm" in m:
            return "qasm_syntax"
        if "test failed" in m or "wrong result" in m or "did not match" in m:
            return "semantic"

        return "unknown"

    try:
        open(logfiledetail, "w", encoding="utf-8").close()
        open(logfile, "w", encoding="utf-8").close()
    except Exception:
        pass

    agent = Tools_Agent(llm_choice=llm_choice, llm_key=llm_key, show=True)

    def _write_and_sync(fh, text):
        fh.write(text)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except Exception:
            pass

    with open(logfiledetail, "a", encoding="utf-8") as f_detail, open(logfile, "a", encoding="utf-8") as f_sum:
        for algo in algos:
            syntax_passes = 0
            final_successes = 0
            total_attempts = 0
            per_attempt_times = []

            algo_prompt_tokens = 0
            algo_completion_tokens = 0
            algo_total_tokens = 0

            for qubitnum in qubitrange:
                for trial in range(max(1, int(avg))):
                    print('=================')
                    print(f'{algo}, {qubitnum}')
                    print(f'trial {trial}')
                    print('=================')

                    total_attempts += 1

                    agent.snapshot_usage()
                    t0 = time.perf_counter()
                    code, record, ok = agent.solve_standard(algo=algo, qubit_num=qubitnum)
                    elapsed = time.perf_counter() - t0
                    per_attempt_times.append(elapsed)
                    print(f'time used: {elapsed:.2f}s')

                    u = agent.usage_since_snapshot()
                    algo_prompt_tokens += u["prompt"]
                    algo_completion_tokens += u["completion"]
                    algo_total_tokens += u["total"]

                    final_successes += int(bool(ok))

                    last_line = record[-1] if record else ""
                    if classify_error(last_line) != "syntax":
                        syntax_passes += 1

                    _write_and_sync(f_detail, f"algo: {algo}, qubitnum: {qubitnum}\nreport detail:\n")
                    for one_record in record:
                        _write_and_sync(f_detail, f"{one_record}\n")
                    _write_and_sync(f_detail, f"time used: {elapsed:.2f}s\n")
                    _write_and_sync(f_detail, f"token usage: prompt={u['prompt']}, completion={u['completion']}, total={u['total']}\n\n")

                    print(f'Token used: {u["total"]}\n')

            denom = len(qubitrange) * max(1, int(avg))
            syntax_rate = 100.0 * (syntax_passes / float(denom)) if denom else 0.0
            final_rate = 100.0 * (final_successes / float(denom)) if denom else 0.0
            avg_time = (sum(per_attempt_times) / len(per_attempt_times)) if per_attempt_times else 0.0

            avg_prompt = (algo_prompt_tokens / denom) if denom else 0.0
            avg_completion = (algo_completion_tokens / denom) if denom else 0.0
            avg_total = (algo_total_tokens / denom) if denom else 0.0

            summary = (
                f"{algo} (qubitnum={qubitrange}): "
                f"syntax pass rate: {syntax_rate:.0f}%, "
                f"finally_success rate: {final_rate:.0f}%, "
                f"avg time: {avg_time:.2f}s, "
                f"avg tokens: prompt={avg_prompt:.0f}, completion={avg_completion:.0f}, total={avg_total:.0f}"
            )
            print(summary)
            _write_and_sync(f_sum, summary + "\n")


if __name__ == "__main__":
    pass