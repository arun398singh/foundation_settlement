import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Default Material Parameters
fck = 25  # Concrete grade in N/mm2
fy = 500  # Grade of steel in N/mm2
soil_bearing_capacity = 250  # kN/m2
E = 20000  # Elastic modulus (from DIN 4019)

# Load-case-specific correction factors (refined from Excel)
load_case_factors = {
    "Crane Operation": 1.25,  # Adjustment based on Excel validation
    "Storm Rear": 1.05,
    "Storm Front": 1.02,
    "During Assembly": 1.3
}

# Streamlit UI
st.title("Foundation Settlement & Tipping Analysis")

# User Input: Dimensions of the footing
L = st.number_input("Enter Length of footing (m):", min_value=1.0, value=7.7)
B = st.number_input("Enter Width of footing (m):", min_value=1.0, value=7.7)
H = st.number_input("Enter Depth of footing (m):", min_value=0.1, value=1.4)

# Load Inputs
loads = {
    "Crane Operation": [5681.0, 65.0, 2975.2],
    "Storm Rear": [6380.0, 150.0, 2925.2],
    "Storm Front": [6980.0, 100.0, 2925.2],
    "During Assembly": [3980.0, 50.0, 2705.2]
}

def calculate_settlement(M, H, V, B, case):
    """
    Calculate settlement at the four corners of the footing.
    """
    e = M / V  # Eccentricity
    f_correction = load_case_factors.get(case, 1.0)  # Use case-specific correction
    
    if e <= B/6:
        sigma_max = (V / (B * L)) * (1 + (6 * e / B))
        sigma_min = (V / (B * L)) * (1 - (6 * e / B))
    else:
        sigma_max = (2 * V) / (B * L)  # Triangular distribution
        sigma_min = 0
    
    # Settlement calculation using refined correction factor
    S = (sigma_max * B * f_correction) / E  
    return S, sigma_max, sigma_min, e

def check_tipping(e, B):
    """
    Check tipping by evaluating eccentricity criteria.
    """
    return "Tipping Risk: YES" if e > B/3 else "Tipping Risk: NO"

def calculate_rotation_angle(M, B, case):
    """
    Calculate the rotation angle using tan formula.
    """
    f_correction = load_case_factors.get(case, 1.0)
    tan_alpha = M / (B * E * f_correction)
    alpha = np.arctan(tan_alpha)  # Convert to radians
    return np.degrees(alpha)  # Convert to degrees

def plot_footing(settlements, eccentricities, rotations):
    """
    Generate a graphical representation of the footing with settlements, eccentricities, and rotations.
    """
    fig, ax = plt.subplots(figsize=(8, 6))  # Increased figure size for spacing
    ax.set_title("Footing Settlement, Eccentricity, and Rotation Representation", pad=20)
    ax.set_xlabel("Footing Length (m)")
    ax.set_ylabel("Footing Width (m)")

    # Define corner positions
    corners = [(0, 0), (L, 0), (L, B), (0, B)]
    labels = ["Corner 1", "Corner 2", "Corner 3", "Corner 4"]

    for i, (x, y) in enumerate(corners):
        ax.scatter(x, y, color='red', label=labels[i] if i == 0 else "")
        ax.text(x, y, f"Settlement: {settlements[i]:.4f} m\nEcc: {eccentricities[i]:.4f} m\nRot: {rotations[i]:.2f}°", 
                fontsize=8, ha='right', va='bottom')
    
    ax.set_xlim(-1, L+1)
    ax.set_ylim(-1, B+1)
    ax.grid(True)
    plt.legend()
    st.pyplot(fig)

if st.button("Run Calculations"):
    settlement_values = []
    eccentricity_values = []
    rotation_values = []
    results = ""
    
    for case, values in loads.items():
        M, H, V = values
        S, sigma_max, sigma_min, e = calculate_settlement(M, H, V, B, case)
        tipping_status = check_tipping(e, B)
        alpha = calculate_rotation_angle(M, B, case)
        results += f"{case}: Settlement = {S:.4f} m, Max Pressure = {sigma_max:.2f} kN/m², {tipping_status}, Rotation Angle = {alpha:.2f}°\n"
        settlement_values.append(S)
        eccentricity_values.append(e)
        rotation_values.append(alpha)
    
    st.text(results)
    plot_footing(settlement_values, eccentricity_values, rotation_values)
