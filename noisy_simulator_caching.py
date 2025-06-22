from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer.noise import NoiseModel
import pickle
from utils import ibm_account_connect

def cache_noise_model(backend_name, filename, instance_name="imperial_ibm_qc"):
    """
    Cache the noise model from a given IBM backend.
    
    Parameters:
    - backend_name: str, e.g., "ibm_torino"
    - filename: str, e.g., "cached_noise_model.pkl"
    - instance_name: str, IBM Quantum instance name
    """
    ibm_account_connect()
    service = QiskitRuntimeService(name = "eddie_ibm_qc")  # corrected key
    backend = service.backend(backend_name)

    noise_model = NoiseModel.from_backend(backend)

    with open(filename, "wb") as f:
        pickle.dump(noise_model, f)

    print(f"[✓] Noise model from {backend_name} saved to {filename}")

devices = {
    "ibm_torino": "heron_model.pkl",
    "ibm_brisbane": "eagle_brisbane_model.pkl",
    "ibm_sherbrooke": "eagle_sherbrooke_model.pkl"
}

for backend_name, file_name in devices.items():
    cache_noise_model(backend_name, file_name)
