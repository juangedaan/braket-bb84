import numpy as np
import time
from braket.circuits import Circuit
from braket.devices import LocalSimulator
import matplotlib.pyplot as plt

# Setting a dynamic random seed based on the current time to ensure different random outcomes in each execution
np.random.seed(int(time.time()))

# Function to encode Alice's message
# In the BB84 protocol, Alice prepares a sequence of qubits in specific quantum states based on randomly chosen bits and bases.
# For each bit, if the chosen basis is Z (0), the qubit is prepared in the computational basis (|0⟩ or |1⟩).
# If the chosen basis is X (1), the qubit is prepared in the superposition basis (|+⟩ or |−⟩).
# This encoding step is crucial for the security of the protocol, as it exploits the quantum properties of superposition and uncertainty.
def encode_message(bits, bases, N):
    message = []
    for i in range(N):
        qc = Circuit()
        # Apply gates based on Alice's bits and bases
        if bases[i] == 0:  # Z-basis
            if bits[i] == 1:
                qc.x(0)
        else:  # X-basis
            if bits[i] == 0:
                qc.h(0)
            else:
                qc.x(0).h(0)
        
        # If no gate is applied (i.e., bit and basis are both 0), add an identity gate
        if len(qc.instructions) == 0:
            qc.i(0)

        message.append(qc)
    return message

# Function to measure the message received by Bob
# Bob, who does not know Alice's basis choice, randomly chooses a basis for each qubit and performs a measurement.
# The choice of basis and the quantum nature of the qubits ensure that Bob's measurements will only sometimes match Alice's encoding if the bases differ.
# This randomness is a key aspect of the protocol, leading to a shared key that is only partially correlated initially.
def measure_message(message, bases, N):
    measurements = []
    device = LocalSimulator()
    for i in range(N):
        qc = message[i].copy()  # Creating a copy of the circuit for measurement
        if bases[i] == 1:  # X-basis chosen by Bob
            qc.h(0)  # Applying Hadamard gate to measure in X-basis
        # The simulator automatically measures all qubits at the end of the circuit
        task = device.run(qc, shots=1)  # Running the circuit on the simulator for a single shot
        result = task.result()  # Getting the result
        measured_bit = result.measurements[0][0]  # Extracting Bob's measured bit
        measurements.append(measured_bit)
    return measurements

# Function to remove bits that don't match in Alice's and Bob's bases
# After the measurement, Alice and Bob publicly compare their bases and discard bits where the bases did not match.
# This sifting process is vital for creating a shared secret key, as it ensures that Alice and Bob only keep correlated bits.
# The length of the final key varies due to the random matching of bases, which is a fundamental characteristic of BB84.
def sift_key(a_bases, b_bases, bits, N):
    sifted_key = []
    for i in range(N):
        if i < len(a_bases) and i < len(b_bases) and i < len(bits):
            if a_bases[i] == b_bases[i]:  # Keeping only bits with matching bases
                sifted_key.append(bits[i])
    return sifted_key

# Set the number of qubits (N) to 8 (or any other desired value within the limits of the simulator)
N = 20

# Alice's random bits and bases
alice_bits = np.random.randint(2, size=N)  # Random bits for Alice
alice_bases = np.random.randint(2, size=N)  # Random bases for Alice
alice_message = encode_message(alice_bits, alice_bases, N)  # Encoding Alice's message

# Bob's bases for measuring the message
bob_bases = np.random.randint(2, size=N)  # Random bases for Bob
bob_measurements = measure_message(alice_message, bob_bases, N)  # Bob measuring the received message

# Sifting the key to get the shared secret key
alice_key = sift_key(alice_bases, bob_bases, alice_bits, N)  # Alice's sifted key
bob_key = sift_key(alice_bases, bob_bases, bob_measurements, N)  # Bob's sifted key

# Visualization and Explanation
# The resulting keys from Alice and Bob should be identical if there was no eavesdropping or interference.
# In real-world applications, additional steps like error correction and privacy amplification would follow to ensure the key's security and integrity.
initial_bits = N
matching_bases_bits = sum(a_base == b_base for a_base, b_base in zip(alice_bases, bob_bases))
final_key_bits = len(alice_key)

# Specify different colors for each bar
colors = ['skyblue', 'salmon', 'lightgreen']
plt.bar(['Initial Bits', 'Matching Bases', 'Final Key'], 
        [initial_bits, matching_bases_bits, final_key_bits], 
        color=colors)
plt.ylabel('Number of Bits')
plt.title('BB84 Key Distillation Process')
plt.show()

print("Alice's key:", alice_key)
print("Bob's key:", bob_key)
print("\nExplanation:")
print(f"Initially, Alice and Bob each generate {initial_bits} bits.")
print(f"After comparing bases, the number of bits with matching bases is {matching_bases_bits}.")
print("During the sifting process, bits with non-matching bases are discarded.")
print(f"The final distilled key contains approximately {final_key_bits} bits, roughly 50% of the initial bits.")
print(f"If there is an evesdropping attempt, or in real life implementations, the final key is always smaller than the matching bases.")
