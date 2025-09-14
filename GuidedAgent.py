from tools import *
import time
from G_Advisor import G_Advisor
from G_Coder import G_Coder
from G_Reviewer import G_Reviewer

from LLM import LLM_model
import traceback
import importlib.util
import os
import random


class Guided_Agent(object):
    def __init__(self, llm_choice='', llm_key='', reflection_round=3, temp=None, candidate_num=3,show=False):
        self.reflection_round = max(0, int(reflection_round))
        self.candidate_num = max(1, int(candidate_num))
        self.show=show
        self.LLM = LLM_model(llm_choice, llm_key, temp=temp)
        self.coder = G_Coder(self.LLM)
        self.advisor = G_Advisor(self.LLM)
        self.reviewer = G_Reviewer(self.LLM)

    def _load_tester(self, algo):

        test_script_path = f'./kernels/{algo}/universal_test.py'
        return load_function_from_script(test_script_path, 'universal_check')

    def _make_record_line(self, cand_idx, trial_idx, success, reason):
        stat = "success" if success else "failed"
        return f"candidate #{cand_idx}, trial #{trial_idx}, {stat}, reason is {reason}"

    def snapshot_usage(self):
        self.LLM.snapshot_usage()

    def usage_since_snapshot(self):
        return self.LLM.usage_since_snapshot()

    def solve_standard(self, algo: str = '', qubit_num: int = 5, shots: int = 3):
        if self.show:
            print(f'solving {algo} when q = {qubit_num}')
        record = []
        final_code = None
        finally_success = False

        tester = self._load_tester(algo)
        self.reviewer.history = []
        self.reviewer.tester = tester

        if self.show:
            print(f'tester loaded for {algo}')

        # Advisor: examples + analysis
        try:
            examples, analysis, _ = self.advisor.conclude_coding_info(algo=algo, shots=shots)
        except Exception as e:
            if self.show:
                print('error of advisor',e)
            record.append(self._make_record_line(0, 0, False, f"advisor failed: {e}"))
            examples, analysis = "", ""

        if self.show:
            print(f'examples extracted for {algo} q = {qubit_num}')
        # Generate multiple candidate codes
        candidates = []
        for i in range(self.candidate_num):
            try:
                candidates.append(self.coder.generate_code(examples, analysis, algo=algo, qubit_num=qubit_num))
            except Exception as e:
                if self.show:
                    print(e)
                record.append(self._make_record_line(i + 1, 1, False, f"generation error: {e}"))
                candidates.append("")


        if self.show:
            print(f'candidates generated for {algo} q = {qubit_num}')
        for ci, code in enumerate(candidates, start=1):
            self.reviewer.history = []
            current_code = code
            for ti in range(1, self.reflection_round + 1):
                if self.show:
                    print(f'this is candidate {ci} reflection round {ti}')
                try:
                    if self.show:
                        print(f'testing and reflecting...')
                    success, message_or_reflection, report = self.reviewer.generate_reflection(current_code, qubit_num=qubit_num)
                    if self.show:
                        print(f'test result is {report}')
                except Exception as e:
                    if self.show:
                        print(e)
                    record.append(self._make_record_line(ci, ti, False, f"reviewer crashed: {e}"))
                    continue
                if success:
                    record.append(self._make_record_line(ci, ti, True, "passed all tests"))
                    final_code = current_code
                    finally_success = True
                    if self.show:
                        print(f'success!')
                    return final_code, record, finally_success

                record.append(self._make_record_line(ci, ti, False, report))
                try:
                    # if self.show:
                    #     print(f'try to rewrite based on reflection: \n{message_or_reflection}\n')
                    current_code = self.coder.regenerate_code(
                        algo=algo,
                        qubit_num=qubit_num,
                        code=current_code,
                        error=report,
                        suggestion=message_or_reflection
                    )
                except Exception as e:
                    if self.show:
                        print(e)
                    record.append(self._make_record_line(ci, ti + 1, False, f"regeneration error: {e}"))
                    continue 

        final_code = candidates[-1] if candidates else None
        if self.show:
            print('failed!')
        return final_code, record, finally_success

    def solve_without_reflection(self, algo: str = '', qubit_num: int = 5, shots: int = 3):
        record = []
        final_code = None
        finally_success = False

        tester = self._load_tester(algo)
        self.reviewer.history = []
        self.reviewer.tester = tester
        try:
            examples, analysis, _ = self.advisor.conclude_coding_info(algo=algo, shots=shots)
        except Exception as e:
            record.append(self._make_record_line(1, 1, False, f"advisor failed: {e}"))
            examples, analysis = "", ""

        try:
            code = self.coder.generate_code(examples, analysis, algo_name=algo, qubit_num=qubit_num)
        except Exception as e:
            record.append(self._make_record_line(1, 1, False, f"generation error: {e}"))
            return None, record, False

        success, _, report = self.reviewer.tester(code,qubit_num)
        if success:
            record.append(self._make_record_line(1, 1, True, "passed all tests"))
            return code, record, True
        else:
            record.append(self._make_record_line(1, 1, False, report))
            return code, record, False

    def solve_without_analysis(self, algo: str = '', qubit_num: int = 5, shots: int = 3,show:bool=False):
        if self.show:
            print(f'solving {algo} when q = {qubit_num}')
        record = []
        final_code = None
        finally_success = False

        tester = self._load_tester(algo)
        self.reviewer.history = []
        self.reviewer.tester = tester

        if self.show:
            print(f'tester loaded for {algo}')
        try:
            examples, analysis, _ = self.advisor.conclude_coding_info(algo=algo, shots=shots)
            analysis='NO AVAILABLE ANALYSIS'
        except Exception as e:
            if self.show:
                print('error of advidor',e)
            record.append(self._make_record_line(0, 0, False, f"advisor failed: {e}"))
            examples, analysis = "", ""

        if self.show:
            print(f'examples extracted for {algo} q = {qubit_num}')
        candidates = []
        for i in range(self.candidate_num):
            try:
                candidates.append(self.coder.generate_code(examples, analysis, algo=algo, qubit_num=qubit_num))
            except Exception as e:
                if self.show:
                    print(e)
                record.append(self._make_record_line(i + 1, 1, False, f"generation error: {e}"))
                candidates.append("")


        if self.show:
            print(f'candidates generated for {algo} q = {qubit_num}')

        for ci, code in enumerate(candidates, start=1):
            self.reviewer.history = []
            current_code = code
            for ti in range(1, self.reflection_round + 1):
                if self.show:
                    print(f'this is candidate {ci} reflection round {ti}')
                try:
                    if self.show:
                        print(f'testing and reflecting...')
                    success, message_or_reflection, report = self.reviewer.generate_reflection(current_code, qubit_num=qubit_num)
                    if self.show:
                        print(f'test result is {report}')
                except Exception as e:

                    if self.show:
                        print(e)
                    record.append(self._make_record_line(ci, ti, False, f"reviewer crashed: {e}"))
                    continue
                if success:
                    record.append(self._make_record_line(ci, ti, True, "passed all tests"))
                    final_code = current_code
                    finally_success = True
                    if self.show:
                        print(f'success!')
                    return final_code, record, finally_success

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
                        print(e)
                    record.append(self._make_record_line(ci, ti + 1, False, f"regeneration error: {e}"))
                    continue

        final_code = candidates[-1] if candidates else None
        if self.show:
            print('failed!')
        return final_code, record, finally_success



#======================the following part is for testing only====================
import time
import os

def run_tests(algos, qubitrange, avg=3, logfile='./log_1.txt', logfiledetail='./log_1_detail.txt', llm_choice='', llm_key=''):
    def classify_error(err_msg):
        try:
            err_msg = (err_msg or "").strip().lower()
        except Exception:
            return "syntax"
        if "passed all tests" in err_msg:
            return "success"
        elif "qasm parsing failed" in err_msg:
            return "syntax"
        else:
            return "semantic"

    # Helper: write + flush + fsync for immediate persistence
    def _write_and_sync(fh, text):
        fh.write(text)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except Exception:
            # On some FS, fsync may not be available; flushing is still helpful
            pass

    # Truncate logs at start so we start fresh
    try:
        open(logfiledetail, "w", encoding="utf-8").close()
        open(logfile, "w", encoding="utf-8").close()
    except Exception:
        pass

    da = Guided_Agent(llm_choice=llm_choice, llm_key=llm_key, show=True)

    # Keep files open for the duration; write immediately after each line/summary
    with open(logfiledetail, "a", encoding="utf-8") as f_detail, open(logfile, "a", encoding="utf-8") as f_sum:
        for algo in algos:
            syntax_passes = 0
            final_successes = 0
            total_attempts = 0
            per_attempt_times = []

            # token accumulators for this algo's block
            algo_prompt_tokens = 0
            algo_completion_tokens = 0
            algo_total_tokens = 0

            for qubitnum in qubitrange:
                for trial in range(max(1, int(avg))):
                    print('=================')
                    print(f'{algo}, {qubitnum}')
                    print(f'trail {trial}')
                    print('=================')

                    total_attempts += 1

                    # snapshot usage before attempt
                    da.snapshot_usage()

                    t0 = time.perf_counter()
                    code, record, ok = da.solve_standard(algo=algo, qubit_num=qubitnum)
                    elapsed = time.perf_counter() - t0
                    per_attempt_times.append(elapsed)
                    print(f'time used: {elapsed:.2f}s')

                    # collect usage delta for this attempt
                    u = da.usage_since_snapshot()
                    algo_prompt_tokens += u["prompt"]
                    algo_completion_tokens += u["completion"]
                    algo_total_tokens += u["total"]

                    final_successes += int(bool(ok))

                    last_line = record[-1] if record else ""
                    if classify_error(last_line) != "syntax":
                        syntax_passes += 1

                    # --- Immediate detailed log writes ---
                    _write_and_sync(f_detail, f"algo: {algo}, qubitnum: {qubitnum}\nreport detail:\n")
                    for one_record in record:
                        _write_and_sync(f_detail, f"{one_record}\n")
                    _write_and_sync(f_detail, f"time used: {elapsed:.2f}s\n")
                    _write_and_sync(f_detail, f"token usage: prompt={u['prompt']}, completion={u['completion']}, total={u['total']}\n\n")

                    print(f'Token used: {u["total"]}\n')

            # Aggregate metrics for this algo
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

def run_tests_write_after_finish(algos, qubitrange, avg=3, logfile='./log_1.txt',logfiledetail='./log_1_detail.txt',llm_choice='',llm_key=''):
    def classify_error(err_msg):
        try:
            err_msg = (err_msg or "").strip().lower()
        except Exception:
            return "syntax"
        if "passed all tests" in err_msg:
            return "success"
        elif "qasm parsing failed" in err_msg:
            return "syntax"
        else:
            return "semantic"

    da = Guided_Agent(llm_choice=llm_choice, llm_key=llm_key, show=True)

    lines = []
    summaries = []
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
                print(f'trail {trial}')
                print('=================')

                total_attempts += 1
                da.snapshot_usage()

                t0 = time.perf_counter()
                code, record, ok = da.solve_standard(algo=algo, qubit_num=qubitnum)
                elapsed = time.perf_counter() - t0
                per_attempt_times.append(elapsed)
                print(f'time used: {elapsed:.2f}s')

                u = da.usage_since_snapshot()
                algo_prompt_tokens += u["prompt"]
                algo_completion_tokens += u["completion"]
                algo_total_tokens += u["total"]

                final_successes += int(bool(ok))

                last_line = record[-1] if record else ""
                if classify_error(last_line) != "syntax":
                    syntax_passes += 1

                lines.append(f"algo: {algo}, qubitnum: {qubitnum}\nreport detail:\n")
                for one_record in record:
                    lines.append(f"{one_record}\n")
                lines.append(f"time used: {elapsed:.2f}s\n")
                lines.append(
                    f"token usage: prompt={u['prompt']}, completion={u['completion']}, total={u['total']}\n"
                )
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
        summaries.append(summary + "\n")

    # Write logs
    try:
        with open(logfiledetail, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        with open(logfile, "w", encoding="utf-8") as f:
            f.write("\n".join(summaries))
    except Exception:
        pass

def run_tests_OLD(algos, qubitrange, avg=3, logfile='./log_1.txt',logfiledetail='./log_1_detail.txt',llm_choice='',llm_key=''):
    def classify_error(err_msg):
        try:
            err_msg = (err_msg or "").strip().lower()
        except Exception:
            return "syntax"
        if "passed" in err_msg:
            return "success"
        elif "qasm parsing failed" in err_msg:
            return "syntax"
        else:
            return "semantic"

    da = Guided_Agent(llm_choice=llm_choice,llm_key=llm_key,show=True)

    lines = []
    summaries=[]
    for algo in algos:
        syntax_passes = 0
        final_successes = 0
        total_attempts = 0

        for qubitnum in qubitrange:
            for trial in range(max(1, int(avg))):
                print('=================')
                print(f'{algo}, {qubitnum}')
                print(f'trail {trial}')
                print('=================')
                total_attempts += 1
                code, record, ok = da.solve_standard(algo=algo, qubit_num=qubitnum)
                final_successes += int(bool(ok))


                last_line = record[-1] if record else ""
                err_type = classify_error(last_line)
                if err_type != "syntax":
                    syntax_passes += 1


                lines.append(f"algo: {algo}, qubitnum: {qubitnum}\nreport detail:\n")
                for one_record in record:
                    lines.append(f"{one_record}\n")

        denom = len(qubitrange) * max(1, int(avg))
        syntax_rate = 100.0 * (syntax_passes / float(denom)) if denom else 0.0
        final_rate = 100.0 * (final_successes / float(denom)) if denom else 0.0
        summary = f"{algo} (qubitnum={qubitrange}): syntax pass rate: {syntax_rate:.0f}%, finally_success rate: {final_rate:.0f}%"
        print(summary)
        summaries.append(summary + "\n")

    # Write logfile
    try:
        with open(logfiledetail, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        with open(logfile, "w", encoding="utf-8") as f:
            f.write("\n".join(summaries))
    except Exception:
        pass


if __name__ == "__main__":
    pass