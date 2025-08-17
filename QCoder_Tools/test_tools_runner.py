#!/usr/bin/env python3
"""
Test script for qcoder_tools_runner.py
"""

import subprocess
import sys
import ast

def test_tools_runner():
    """Test the qcoder_tools_runner.py script"""
    
    # Simple test question
    question = "Design a quantum circuit to create a Bell state with 2 qubits"
    qubit_n = 2
    
    # Build command
    cmd = [
        sys.executable, 
        'qcoder_tools_runner.py',
        '--question', question,
        '--qubit_n', str(qubit_n),
        '--reflection_round', '1',  # Use fewer rounds for testing
        '--candidate_num', '1'
    ]
    
    print("Testing qcoder_tools_runner.py...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run the subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            # Parse the output
            success = False
            reports_dict = {}
            codes_dict = {}
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith('SUCCESS: '):
                    success = line.split('SUCCESS: ')[1].strip() == 'True'
                elif line.startswith('REPORTS_DICT: '):
                    reports_str = line.split('REPORTS_DICT: ')[1].strip()
                    try:
                        reports_dict = ast.literal_eval(reports_str)
                    except:
                        reports_dict = {}
                elif line.startswith('CODES_DICT: '):
                    codes_str = line.split('CODES_DICT: ')[1].strip()
                    try:
                        codes_dict = ast.literal_eval(codes_str)
                    except:
                        codes_dict = {}
            
            print("✓ Successfully parsed output")
            print(f"✓ Success: {success}")
            print(f"✓ Generated {len(codes_dict)} code versions")
            print(f"✓ Generated {len(reports_dict)} reports")
            return True
        else:
            print(f"✗ Subprocess failed with return code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Subprocess timed out")
        return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_tools_runner()
    if success:
        print("\n✓ Test passed!")
    else:
        print("\n✗ Test failed!")
        sys.exit(1) 