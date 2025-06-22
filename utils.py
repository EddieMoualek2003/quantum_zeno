from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit import transpile
import pickle

## Module Imports
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit.primitives import StatevectorSampler

def ibm_account_connect():
    token = "4Ke_JAy6uepzHTBV9fSDjGbFrSse7VYWwRgHJULxx34q"
    instance = "crn:v1:bluemix:public:quantum-computing:us-east:a/737dfb0b1e374ec7a5772fdbcece5643:a48276b9-a41b-449c-8d76-d2adf66ea9d4::"
    try:
        QiskitRuntimeService.save_account(
        token=token,
        channel="ibm_cloud", # `channel` distinguishes between different account types.
        instance=instance, # Copy the instance CRN from the Instance section on the dashboard.
        name="eddie_ibm_qc", # Optionally name this set of credentials.
        overwrite=True # Only needed if you already have Cloud credentials.
        )
        print("Account Created - Continuing.")
    except:
        print("Account Exists - Continuing.")
    return None

def noisy_local_simulator(qc):
    # Use fake noisy backend
    fake_backend = FakeManilaV2()
    noise_model = NoiseModel.from_backend(fake_backend)
    simulator = AerSimulator(noise_model=noise_model)

    # Transpile circuit
    qc_t = transpile(qc, simulator)
    # Run simulation
    shots = 4096
    # Note: shots is set to 1024, but can be adjusted as needed.
    job = simulator.run(qc_t, shots=shots)
    result = job.result()
    counts = result.get_counts()
    return dict(sorted(counts.items(), key=lambda x: int(x[0], 2)))

def load_model_from_file():
    filename = "cached_noise_model.pkl"
    with open(filename, "rb") as f:
        noise_model = pickle.load(f)
    return noise_model

def noisy_remote_simulator(qc):
    shots = 4096
    noise_model = load_model_from_file()
    simulator = AerSimulator(noise_model=noise_model)
    qc_t = transpile(qc, simulator)
    job = simulator.run(qc_t, shots=shots)
    result = job.result()
    counts = result.get_counts()
    return dict(sorted(counts.items(), key=lambda x: int(x[0], 2)))

def ibm_quantum_backend(qc):
    # ibm_account_connect()

    ## Run on the quantum computer.
    service = QiskitRuntimeService(name="eddie_ibm_qc")

    backend = service.least_busy(simulator=False, operational=True, min_num_qubits=1)
    sampler = Sampler(mode=backend)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    ## Transpilation of the current circuit.
    isa_circuit = pm.run(qc)
    ## Run the job on the quantum computer
    job = sampler.run([isa_circuit])
    pub_result = job.result()
    # print("Job Complete")
    counts = pub_result[0].data.meas.get_counts()

    return dict(sorted(counts.items(), key=lambda x: int(x[0], 2)))


def prepare_measurements(qc, num_qubits):
    """Return three versions of the circuit with correct measurement syntax."""
    qc_local = qc.copy()
    qc_remote = qc.copy()
    qc_quantum = qc.copy()

    # Apply explicit measurement
    qc_local.measure(range(num_qubits), range(num_qubits))
    qc_remote.measure(range(num_qubits), range(num_qubits))

    # measure_all auto-adds classical bits
    qc_quantum.measure_all()

    return qc_local, qc_remote, qc_quantum


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