from tools import *
from LLM import LLM_model



class Calibrator:
    def __init__(self, llm):

        self.llm = llm
        # self.llm.generate(prompt, system_prompt, 10240)

        self.system_prompt_generate="You are an AI assistant who outputs json content based on user's requirements"

    def generate_calibration_instructions(self, description):

        # OPTION0: use function call, but not all models support function calling. 
        # OPTION1: let llm to generate a json script whether to call a calibrate(qubit, param_name, value) and thedetailed params. *CHOSEN
        # OPTION2: directly generate python code then execute

        hint="""
        **the hint of how to determine variable name: 

        the frequency of qubit-0 = q0_freq
        qubit-8's frequency = q9_freq
        readout frequency of 5th qubit = ro5_freq
        the readout frequency of qubit-3 = ro3_freq


        **example 1 of user's input is:

        I want to calibrate qubit-1 with new frequency 4.878e9, and readout frequency of qubit-17 as 6.89e9.

        **the corresponding example 1 output is:

        [
          {
            "variable_name": "q1_freq",
            "value": 4.87e9
          },
          {
            "variable_name": "ro17_freq",
            "value": 6.89e9
          }
        ]

        **example 2 of user's input is:

        calibrate qubit-9' frequency as 5.22e9.

        **the corresponding example 2 output is:

        [
          {
            "variable_name": "q9_freq",
            "value": 5.22e9
          },
        ]
        """
        prompt=f"""the user's requirement is:

        {description}

        now generate the json content without anything else:
        """

        instr=self.llm.generate(hint+'\n'+prompt, self.system_prompt_generate,max_tokens=10240)
        return instr


if __name__ == "__main__":
    pass