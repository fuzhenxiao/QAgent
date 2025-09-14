from tools import *
from LLM import LLM_model
import traceback
import importlib.util
import os
import random
import json
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

 


if __name__ == "__main__":
    pass