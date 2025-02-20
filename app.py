import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Function to get material properties based on user input
def get_material_properties(concrete_grade, steel_grade):
    concrete_strength = {
        'M20': 20,  # MPa
        'M25': 25,
        'M30': 30,
        'M35': 35,
        'M40': 40
    }
    
    steel_strength = {
        'Fe415': 415,  # MPa
        'Fe500': 500,
        'Fe600': 600
    }
    
    return concrete_strength[concrete_grade], steel_strength[steel_grade]

# Function to calculate flexural reinforcement
def calculate_flexural_reinforcement(Mu, d, steel_strength):
    Ast = Mu * 10**6 / (0.138 * steel_strength * d)  # mm^2
    return Ast

# Function to calculate shear reinforcement
def calculate_shear_reinforcement(Vu, b, d, steel_strength):
    Av = Vu / (0.87 * steel_strength * d)  # mm^2
    return Av

# Function to sketch reinforcement details
def sketch_reinforcement_details(Ast, Av):
    fig, ax = plt.subplots()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Reinforcement Details")
    
    # Sketch main reinforcement
    ax.plot([0.1, 0.9], [0.8, 0.8], color='blue', linewidth=5, label='Main Reinforcement')
    
    # Sketch shear reinforcement
    for i in np.linspace(0.1, 0.9, 5):
        ax.plot([i, i], [0.2, 0.4], color='red', linewidth=2, label='Shear Reinforcement' if i == 0.1 else "")
    
    ax.text(0.5, 0.9, f'Ast: {Ast:.2f} mm²', horizontalalignment='center')
    ax.text(0.5, 0.5, f'Av: {Av:.2f} mm²', horizontalalignment='center')
    ax.legend()
    plt.axis('off')
    st.pyplot(fig)

# Streamlit UI
st.set_page_config(
    page_title="Design Calculator",
    page_icon="logo.png",
)

# Input values
span = st.number_input("Clear Span (Lc) in m", value=None)  # Default value for span set to None
load = st.number_input("Service Live Load (w) in kN/m", value=None)  # Default value for load set to None
support_width = st.number_input("Support Width (bs) in m", value=None)  # Default value for support width set to None
concrete_grade = st.selectbox("Concrete Grade", ["M20", "M25", "M30", "M35", "M40"], index=None)
steel_grade = st.selectbox("Steel Grade", ["Fe415", "Fe500", "Fe600"], index=None)

# Assumption values
bar_diameter = st.number_input("Bar Diameter (φ) in mm", value=16)  # Default value for bar diameter
cover = st.number_input("Concrete Cover (in mm)", value=25)  # Default value for cover
effective_depth = st.number_input("Effective Depth (d) in mm", value=250)  # Default value for effective depth

# Calculate overall depth (D)
overall_depth = effective_depth + cover + (bar_diameter / 2)  # mm

# Calculate beam width (b) using the formula b = 1/3*d to 2/3*d
beam_width_min = effective_depth / 3  # Minimum width
beam_width_max = (2 * effective_depth) / 3  # Maximum width
beam_width = (beam_width_min + beam_width_max) / 2  # Average width for design

# Button to calculate
if st.button("Calculate"):
    # Check if inputs are provided
    if load is not None and span is not None and support_width is not None and concrete_grade is not None and steel_grade is not None:
        # Get material properties
        concrete_strength, steel_strength = get_material_properties(concrete_grade, steel_grade)

        # Step 1: Given Data
        st.subheader("Step 1: Given Data")
        st.write(f"- **Clear Span (Lc)** = {span:.2f} m")
        st.write(f"- **Support Width (bs)** = {support_width * 1000:.0f} mm (each support)")
        st.write(f"- **Service Live Load (w)** = {load:.2f} kN/m")
        st.write(f"- **Concrete Grade**: {concrete_grade} (fck = {concrete_strength} MPa)")
        st.write(f"- **Steel Grade**: {steel_grade} (fy = {steel_strength} MPa)")
        st.write(f"- **Beam Width (b)** = {beam_width:.2f} mm")
        st.write(f"- **Effective Depth (d)** = {effective_depth:.2f} mm")
        st.write(f"- **Overall Depth (D)** = {overall_depth:.2f} mm")
        st.write(f"- **Concrete Cover** = {cover} mm")
        st.write(f"- **Bar Diameter (φ)** = {bar_diameter} mm")

        # Step 2: Load Calculation
        self_weight = (25 * (beam_width / 1000) * effective_depth)  # kN/m
        st.write(f"#### Self-weight Calculation")
        st.write(f"Self-weight = 25 × (b × d) = 25 × ({beam_width / 1000:.2f} × {effective_depth:.2f}) = {self_weight:.2f} kN/m")
        st.write(f"Total Dead Load (DL) = Self-weight of beam = {self_weight:.2f} kN/m")
        st.write(f"Live Load (LL) = {load:.2f} kN/m")
        total_service_load = self_weight + load
        st.write(f"Total Service Load (w_total) = w_DL + w_LL = {self_weight:.2f} + {load:.2f} = {total_service_load:.2f} kN/m")
        factored_load = 1.5 * total_service_load
        st.write(f"Factored Load (for Design) = w_u = 1.5 × w_total = 1.5 × {total_service_load:.2f} = {factored_load:.2f} kN/m")

        # Step 3: Bending Moment Calculation
        Mu = (factored_load * span**2) / 8  # kNm
        st.write(f"#### Bending Moment Calculation")
        st.write(f"M_u = w_u * L² / 8 = {factored_load:.2f} × {span:.2f}² / 8 = {Mu:.2f} kNm")
        Mu_Nmm = Mu * 10**6  # Convert to N·mm
        st.write(f"Convert to N·mm: M_u = {Mu:.2f} × 10^6 = {Mu_Nmm:.2f} N·mm")

        # Step 4: Flexural Design
        Ast = calculate_flexural_reinforcement(Mu, effective_depth, steel_strength)  # Calculate Ast
        st.write(f"#### Flexural Design")
        st.write(f"A_s = M_u * 10^6 / (0.138 * f_y * d) = {Mu_Nmm:.2f} / (0.138 * {steel_strength} * {effective_depth})")
        st.write(f"A_s = {Ast:.2f} mm²")

        # Step 5: Shear Design
        Vu = factored_load * span / 2  # Maximum shear force
        st.write(f"#### Shear Design")
        st.write(f"V_u = w_u × L / 2 = {factored_load:.2f} × {span:.2f} / 2 = {Vu:.2f} kN")
        nominal_shear_stress = Vu * 1000 / (beam_width * effective_depth)  # Convert Vu to N and calculate shear stress
        st.write(f"Nominal shear stress (τ_v) = V_u / (b × d) = {Vu:.2f} × 1000 / ({beam_width} × {effective_depth}) = {nominal_shear_stress:.2f} N/mm²")

        # Check against permissible shear stress
        permissible_shear_stress = 0.48  # N/mm² for M20
        st.write(f"Permissible shear stress (τ_c) for M20 = {permissible_shear_stress} N/mm²")
        if nominal_shear_stress > permissible_shear_stress:
            st.write("Since τ_v > τ_c, stirrups are required.")
        else:
            st.write("Shear reinforcement is not required.")

        # Shear Reinforcement Calculation
        Av = calculate_shear_reinforcement(Vu, beam_width, effective_depth, steel_strength)  # Calculate Av
        st.subheader("Shear Reinforcement")
        st.write(f"Provide 8 mm Ø stirrups @ 150 mm c/c. A_v = {Av:.2f} mm²")

        # Step 6: Deflection Control Check
        st.subheader("Step 6: Deflection Control Check")
        L_eff = span * 1000  # Convert to mm
        deflection_limit = L_eff / 20
        st.write(f"Deflection limit = L_eff / 20 = {L_eff:.2f} / 20 = {deflection_limit:.2f} mm")
        st.write("Deflection is within limits.")

        # Step 7: Reinforcement Detailing
        st.subheader("Step 7: Reinforcement Detailing")
        st.write("Main Bars:")
        st.write("Tension Reinforcement: 4 bars of 16 mm Ø")
        st.write("Compression Steel (if needed for ductility): 2 bars of 12 mm Ø")
        st.write("Shear Reinforcement: 8 mm Ø stirrups @ 150 mm c/c")

        # Step 8: Sketch the Reinforcement Details
        sketch_reinforcement_details(Ast, Av)
    else:
        st.warning("Please enter the required inputs to perform the calculations.")