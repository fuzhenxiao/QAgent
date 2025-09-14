
# The reviewer within Guided-few-shot Coding Agent
class G_Reviewer(object):
    """
      On success: records attempt, returns (True, "The code is verified as successful.").
      On failure: records attempt, builds a reflection prompt using history (previousfailed attempts + current error), returns (False, reflection).
    """

    def __init__(self, llm, system_prompt= None, max_history = 10):
        self.llm = llm
        self.tester = None  # to be set externally
        self.max_history = max_history

        # Tight, typo-free system prompt focused on QASM 3.0 reflection.
        self.system_prompt = system_prompt or (
            "You are an expert in quantum programming, especially QASM 3.0. "
            "Analyze compiler/runtime errors and propose suggestion for fixes. "
            "Output ONLY one section:\n"
            "Analysis:\n"
            "Keep it concise but technically accurate. You don't need to show the code.Only suggestion is needed"
        )

        # Each item: {"code": str, "report": str, "success": bool}
        self.history: List[Dict[str, Any]] = []

    def _add_to_history(self, code, report, success):
        self.history.append({"code": code, "report": report, "success": success})
        # Trim to most recent N attempts
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def _build_reflection_prompt(self, code, report):

        prior_failures = [h for h in self.history if not h.get("success", False)]

        # Summarize prior context
        history_section = []
        for i, h in enumerate(prior_failures[-(self.max_history - 1):], start=1):
            history_section.append(
                f"Attempt {i}:\n"
                f"Code:\n{h['code']}\n"
                f"Error/Report:\n{h['report']}\n"
            )

        history_block = ""
        if history_section:
            history_block = "Previous failed attempts (most recent last):\n" + "\n".join(history_section) + "\n"

        # Current attempt goes last
        current_block = (
            "Current attempt:\n"
            f"Code:\n{code}\n"
            f"Error/Report:\n{report}\n"
        )

        # Final instruction
        tail_instruction = (
            "Now analyze the error context and propose a fix.\n"
            "Provide ONLY:\n"
            "Analysis:\n"
            "You don't need to show the code.Only suggestion is needed"
        )

        return f"{history_block}{current_block}\n{tail_instruction}"

    def generate_reflection(self, code,qubit_num):
        """
        Returns:
        (True, 'The code is verified as successful.',report) on success
        (False, '<reflection text>',report) on failure
        """
        if self.tester is None:
            raise RuntimeError("Reviewer.tester is not set. Please assign a tester callable before use.")

        issuccess, _, report = self.tester(code,qubit_num)


        self._add_to_history(code=code, report=report, success=issuccess)

        if issuccess:
            return True, "The code is verified as successful.",report

        prompt = self._build_reflection_prompt(code, report)

        # Ask LLM for analysis/solution (reflection)
        try:
            reflection = self.llm.generate(
                prompt,
                self.system_prompt,
                max_tokens=512
            )
        except Exception as e:
            reflection = (
                "Analysis:\n"
                f"LLM reflection failed with error: {e}\n"
                "Based on the tester report, investigate the issues above.\n\n"
                "Solution:\n"
                "Address the reported errors, re-run tests, and iterate."
            )

        return False, reflection,report


# === Test Code ===
if __name__ == "__main__":
    pass
