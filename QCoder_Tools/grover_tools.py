import math
from io import StringIO
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump, loads
from qiskit_aer import AerSimulator
import random
# 生成 Grover Oracle
def create_grover_oracle(n, marked_state):
    oracle = QuantumCircuit(n)
    rev_target = marked_state[::-1]
    zero_inds = [i for i, c in enumerate(rev_target) if c == "0"]
    if zero_inds:
        oracle.x(zero_inds)
    oracle.h(n - 1)
    oracle.mcx(list(range(n - 1)), n - 1)
    oracle.h(n - 1)
    if zero_inds:
        oracle.x(zero_inds)
    oracle_gate = oracle.to_gate()
    oracle_gate.name = "Oracle"
    return oracle_gate

# 生成 Grover 电路
def generate_grover_circuit(n):
    num_iterations = math.floor(math.pi / 4 * math.sqrt(2 ** n))
    circuit = QuantumCircuit(n, n)
    circuit.h(range(n))
    diffuser = create_diffusion_operator(n)
    for _ in range(num_iterations):
        circuit.barrier()
        circuit.append(diffuser, range(n))
    circuit.measure(range(n), range(n))
    return circuit

# 生成 Diffusion Operator
def create_diffusion_operator(n):
    diffuser = QuantumCircuit(n)
    diffuser.h(range(n))
    diffuser.x(range(n))
    diffuser.h(n - 1)
    diffuser.mcx(list(range(n - 1)), n - 1)
    diffuser.h(n - 1)
    diffuser.x(range(n))
    diffuser.h(range(n))
    diffuser_gate = diffuser.to_gate()
    diffuser_gate.name = "Diffuser"
    return diffuser_gate

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def combine_oracle_with_circuit(circuit, oracle_gate, num_iterations=None):
    n = circuit.num_qubits
    if num_iterations is None:
        num_iterations = math.floor(math.pi / 4 * math.sqrt(2 ** n))
    diffuser = create_diffusion_operator(n)
    combined = QuantumCircuit(n, n)
    combined.h(range(n))
    for _ in range(num_iterations):
        combined.append(oracle_gate, range(n))
        combined.append(diffuser, range(n))
    combined.measure(range(n), range(n))
    return combined
    
def test_grover_circuit(circuit_template, n, shots=100):
    aer_sim = AerSimulator()
    all_states = [format(i, f"0{n}b") for i in range(2 ** n)]
    if n >= 5:
        all_states = random.sample(all_states, 32)

    success_count = 0
    for marked_state in all_states:
        oracle_gate = create_grover_oracle(n, marked_state)
        circuit_with_oracle = combine_oracle_with_circuit(circuit_template, oracle_gate)
        transpiled = transpile(circuit_with_oracle, aer_sim)
        result = aer_sim.run(transpiled, shots=shots).result()
        counts = result.get_counts()
        predicted = max(counts, key=counts.get)
        if predicted == marked_state:
            success_count += 1

    success_rate = success_count / len(all_states)
    passed = success_count == len(all_states)
    return passed, success_rate


# 测试单个 Oracle
def test_grover_oracle(n, oracle_gate, shots=100):
    aer_sim = AerSimulator()
    circuit = combine_oracle_with_circuit(generate_grover_circuit(n), oracle_gate)
    transpiled = transpile(circuit, aer_sim)
    result = aer_sim.run(transpiled, shots=shots).result()
    counts = result.get_counts()
    predicted = max(counts, key=counts.get)
    return predicted

# 主程序
if __name__ == "__main__":
    n = 5  # 可调整 qubit 数
    bare_circuit = generate_grover_circuit(n)
    passed, success_rate = test_grover_circuit(bare_circuit, n, shots=100)
    if passed:
        print(f"✅ Grover circuit passed: {success_rate * 100:.1f}% success")
    else:
        print(f"⚠️ Grover circuit partial pass: {success_rate * 100:.1f}% success")


    print("\n🔧 Testing individual oracles...")
    all_states = [format(i, f"0{n}b") for i in range(2 ** n)]
    test_states = all_states if n < 5 else random.sample(all_states, 16)

    for marked_state in test_states:
        oracle_gate = create_grover_oracle(n, marked_state)
        predicted = test_grover_oracle(n, oracle_gate, shots=100)
        if predicted == marked_state:
            print(f"✅ Oracle {marked_state} passed, predicted: {predicted}")
        else:
            print(f"⚠️ Oracle {marked_state} failed, predicted: {predicted}")
