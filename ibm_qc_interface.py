## Module Imports
import pickle
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit import transpile

def noisy_remote_simulator_2(qc, model_file="cached_noise_model.pkl", shots=4096):
    """
    Run a noisy simulation using a cached noise model from file.

    Parameters:
    - qc: QuantumCircuit to simulate
    - model_file: Path to the cached noise model (.pkl file)
    - shots: Number of shots to simulate

    Returns:
    - dict: Sorted measurement counts
    """
    # Load noise model from file
    with open(model_file, "rb") as f:
        noise_model = pickle.load(f)

    # Prepare simulator
    simulator = AerSimulator(noise_model=noise_model)

    # Transpile and simulate
    qc_t = transpile(qc, simulator)
    result = simulator.run(qc_t, shots=shots).result()
    counts = result.get_counts()

    # Return counts sorted by bitstring
    return dict(sorted(counts.items(), key=lambda x: int(x[0], 2)))