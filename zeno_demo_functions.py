from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from math import *
import pickle
import matplotlib.pyplot as plt
from ibm_qc_interface import *


## This function is responsible for returning pairs that will be used to place measurements after certain numbers of operations
def returnFactors(numOperators):
    factors = []
    for i in range(1,numOperators+1):
        if numOperators%i == 0:
            factors.append(i)
    factorPairs = []
    
    for i in range(int(len(factors)/2)):
        factorPairs.append([factors[i], factors[len(factors)-1-i]])
        factorPairs.append([factors[len(factors)-1-i], factors[i]])

    if len(factors)%2 != 0:
        factorPairs.append([int(sqrt(numOperators)), int(sqrt(numOperators))])
    return factorPairs



# def create_circuit(numOperators, theta):
#     qc1 = QuantumCircuit(1, 1)
#     for i in range(numOperators):
#         qc1.ry(theta, 0)
#     qc1.measure(0, 0)
#     return qc1

def create_circuit(numOperators, theta):
    """
    Builds a circuit that applies numOperators stages of evolution,
    each followed by a measurement to simulate the Quantum Zeno effect.
    """
    qc = QuantumCircuit(1, 1)

    # Split total angle into smaller steps
    d_theta = theta / numOperators

    for _ in range(numOperators):
        qc.ry(d_theta, 0)   # Partial evolution
        qc.measure(0, 0)    # Simulate collapse
        qc.reset(0)         # Reset to |0⟩ for next stage

    # Optional: add one final measurement to record the state
    qc.measure(0, 0)

    return qc



def zeno_data_analysis(xeno_qc_structure):
    # Access the dictionary contents properly
    circuits = xeno_qc_structure['QC']
    probabilities = xeno_qc_structure['P']
    factorArray = xeno_qc_structure['dim']

    # for i, circuit in enumerate(circuits):
    #     fig = circuit.draw("mpl")
    #     fig.savefig(f"resource_folder/zeno_quantum_circuit{i}.png")

    return [probabilities, [row[1] for row in factorArray]]

def write_pickle(zeno_qc_structure, numOperators, backend = "simulator"):
    # with open(f"resource_folder/quantum_zeno_data_num_op{numOperators}_{backend}.pkl", "wb") as f:
    #     pickle.dump(zeno_qc_structure, f)
    return 0

def process_circuit(numOpPerStage, noisy=False):
    probabilityArray = []
    circuit = create_circuit(numOpPerStage, theta=pi/2) # Create the circuit with the number of operators and theta value
    # print("Circuit Created")

    s1 = noisy_remote_simulator_2(circuit, "heron_model.pkl")
    shots = 4096
    # if noisy:
    #     print("Noisy Simulator Mode")
    #     # Run the circuit on the noisy simulator
    #     s1, shots = noisy_simulator(circuit)
    # else:
    #     print("Ideal Simulator Mode")
    #     # Run the circuit on the ideal simulator
    #     s1, shots = ideal_simulator(circuit)
    numZero = list(s1.values())[list(s1.keys()).index('0')] # Find the occurence of 0
    p = numZero/shots # Calculate the probability of measuring the zero state
    return s1, circuit, probabilityArray, p

def zeno_demo_main(numOperators = 4):
    # Everything will be run on the simulator, so set this to True.
    simulator = True
    probabilityGroup = []
    circuitGroup = []
    factorArray = returnFactors(numOperators)
    for factorPair in factorArray:
        numOpPerStage = factorPair[0]
        numIter = factorPair[1]
        for i in range(numIter): # Repeat for all the iterations needed
            print(f">>> # Operators: {numOperators}, # Iterations: {numIter}, Current Iteration: {i + 1}")
            s1, circuit, probabilityArray, p = process_circuit(numOpPerStage=numOpPerStage, noisy=True)

            # numZero = list(s1.values())[list(s1.keys()).index('0')] # Find the occurence of 0
            # p = numZero/4096
            # print(f"Probability of Zero State is {p}")
            if i < numIter - 1:
                if p > 0.5: # This means the state has not changed from the 0 state yet.
                    probabilityArray.append(p)
                else: # This means the system has changed state
                    probabilityArray.append(1-p)
                    break
            elif i == numIter-1:
                probabilityArray.append(1-p)
                break
            print(probabilityArray)
        circuitGroup.append(circuit)
        probabilityGroup.append(probabilityArray)
    zeno_qc_structure = {
        "QC"    :   circuitGroup, 
        "P"     :   probabilityGroup,
        "dim"   :   factorArray
    }
    [x, y] = zeno_data_analysis(zeno_qc_structure)

    # Create the figure and plot
    fig, ax = plt.subplots()
    ax.scatter(y, x)
    ax.set_title("Probability of State Change")
    ax.set_xlabel("Number of Measurements")
    ax.set_ylabel("Probability of State Change (Time Evolution)")
    ax.set_xlim(0, int(numOperators)+2)
    ax.set_ylim(0, 1)

    # Save the figure
    backend = "simulator" if simulator else "QC"
    plt.savefig(f"resource_folder/zeno_probability_plot.png", dpi=1024, bbox_inches='tight')

    # Optional: display the plot
    # plt.show()

    write_pickle(zeno_qc_structure=zeno_qc_structure, numOperators=numOperators, backend=backend)  

    return zeno_qc_structure