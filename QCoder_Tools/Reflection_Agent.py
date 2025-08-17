
from tools import RAG,SearchEngine
from LLM import LLM_model
import os
import glob
import re



class ReflectionAgent:
    def __init__(self, llm):
        self.llm = llm

    def reflect_and_revise(self, question, plan_agent_out, executor_report):
        system_prompt = """
You are a reflection agent. Given:
1. The original user question.
2. The current plan and code.
3. The executor report (including success/failure).

Your task:
- If the executor report says SUCCESS, just output:
SUCCESS

- If the executor report says FAILURE, output exactly in this format:
- Please mind, do not include any comments or notes in code section!
- there should only be code after 'REVISED CODE', nothing else!
REVISED PLAN:
(new plan text)
REVISED CODE:
(new Python code text)
"""
        # Compose message
        question_text = f"<<QUESTION>>\n{question}\n<<END QUESTION>>"
        tools_text = f"<<TOOLS>>\n{plan_agent_out['tools']}\n<<END TOOLS>>"
        plan_text = f"<<PLAN>>\n{plan_agent_out['plan']}\n<<END PLAN>>"
        code_text = f"<<CODE>>\n{plan_agent_out['code']}\n<<END CODE>>"
        report_text = f"<<REPORT>>\n{executor_report}\n<<END REPORT>>"

        llm_input = f"{question_text}\n\n{tools_text}\n\n{plan_text}\n\n{code_text}\n\n{report_text}"

        llm_response = self.llm.generate(llm_input, system_prompt, max_tokens=1500).strip()

        if llm_response.startswith("SUCCESS"):
            return {'success': True, 'plan': plan_agent_out['plan'], 'code': plan_agent_out['code']}
        elif llm_response.startswith("REVISED PLAN:"):
            try:
                plan_part = llm_response.split("REVISED PLAN:")[1].split("REVISED CODE:")[0].strip()
                code_part = llm_response.split("REVISED CODE:")[1].strip()
                return {'success': False, 'plan': plan_part, 'code': code_part}
            except Exception as e:
                return {'success': False, 'plan': plan_agent_out['plan'], 'code': plan_agent_out['code'], 'error': f"Failed to parse reflection: {str(e)}"}
        else:
            return {'success': False, 'plan': plan_agent_out['plan'], 'code': plan_agent_out['code'], 'error': "Unrecognized reflection output"}




    
    
