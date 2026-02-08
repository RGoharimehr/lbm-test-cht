"""
Example 9: Dimensionless Scaling for High Reynolds Number Simulations

This example demonstrates how to properly scale LBM simulations to achieve
high Reynolds numbers while maintaining numerical stability.

Key concepts:
1. LBM constraints: Ma < 0.3, tau > 0.6
2. Freedom: Can adjust domain size N, dx, dt
3. Goal: Achieve target Re while satisfying constraints
"""
import sys
sys.path.insert(0, '/home/runner/work/lbm-test-cht/lbm-test-cht')

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht.lbm.unit_converter import DimensionlessScaling


def example_moderate_reynolds():
    """
    Example 1: Moderate Reynolds number (Re = 1000)
    This is achievable with reasonable grid sizes.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Moderate Reynolds Number (Re = 1000)")
    print("="*70)
    
    # Physical parameters
    u_phys = 0.1  # m/s (moderate velocity)
    D_phys = 0.01  # m (10 mm diameter)
    nu_water = 1.0e-6  # m²/s
    
    Re_phys = u_phys * D_phys / nu_water
    print(f"\nPhysical parameters:")
    print(f"  Velocity: {u_phys} m/s")
    print(f"  Diameter: {D_phys*1000} mm")
    print(f"  Reynolds: {Re_phys:.0f}")
    
    # Create scaling with conservative Ma
    scaling = DimensionlessScaling(
        Re_target=Re_phys,
        L_ref=D_phys,
        u_ref=u_phys,
        nu_ref=nu_water,
        Ma_target=0.1,
        tau_target=0.7
    )
    
    print(f"\nResult: Domain size N = {scaling.N} lattice units")
    print(f"This is practical for simulations!")
    
    return scaling


def example_high_reynolds_adjust_velocity():
    """
    Example 2: High Reynolds number by adjusting velocity
    Show how to achieve Re=10,000 with different Ma targets.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: High Reynolds Number (Re = 10,000) - Velocity Adjustment")
    print("="*70)
    
    # Physical parameters
    u_phys = 1.0  # m/s
    D_phys = 0.01  # m (10 mm)
    nu_water = 1.0e-6  # m²/s
    Re_target = 10000
    
    print(f"\nTarget Reynolds: {Re_target}")
    print(f"\nTrying different Mach number targets:")
    
    results = []
    for Ma in [0.05, 0.1, 0.15, 0.2]:
        print(f"\n  Ma = {Ma}:")
        scaling = DimensionlessScaling(
            Re_target=Re_target,
            L_ref=D_phys,
            u_ref=u_phys,
            nu_ref=nu_water,
            Ma_target=Ma,
            tau_target=0.7
        )
        print(f"    Domain size: N = {scaling.N}")
        print(f"    Grid spacing: dx = {scaling.dx*1e6:.2f} μm")
        results.append((Ma, scaling.N, scaling.dx))
    
    # Show trade-off
    print(f"\nTrade-off: Higher Ma → Smaller domain, but less stable")
    print(f"Recommended: Ma = 0.1 for best balance")
    
    return results


def example_high_reynolds_adjust_tau():
    """
    Example 3: High Reynolds number by adjusting tau
    Show how tau affects domain size.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: High Reynolds Number (Re = 10,000) - Tau Adjustment")
    print("="*70)
    
    # Physical parameters
    u_phys = 1.0  # m/s
    D_phys = 0.01  # m
    nu_water = 1.0e-6  # m²/s
    Re_target = 10000
    
    print(f"\nTarget Reynolds: {Re_target}")
    print(f"Fixed Ma = 0.1")
    print(f"\nTrying different tau values:")
    
    results = []
    for tau in [0.55, 0.6, 0.7, 0.8, 1.0]:
        stability = "⚠ Marginal" if tau < 0.6 else "✓ Stable"
        print(f"\n  tau = {tau} ({stability}):")
        scaling = DimensionlessScaling(
            Re_target=Re_target,
            L_ref=D_phys,
            u_ref=u_phys,
            nu_ref=nu_water,
            Ma_target=0.1,
            tau_target=tau
        )
        print(f"    Domain size: N = {scaling.N}")
        print(f"    Grid spacing: dx = {scaling.dx*1e6:.2f} μm")
        results.append((tau, scaling.N, scaling.dx))
    
    print(f"\nTrade-off: Lower tau → Smaller domain, but less stable")
    print(f"Recommended: tau = 0.7 for good stability")
    
    return results


def example_very_high_reynolds():
    """
    Example 4: Very high Reynolds number (Re = 100,000)
    Show that extreme Re requires compromises.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Very High Reynolds Number (Re = 100,000)")
    print("="*70)
    
    # Physical parameters  
    u_phys = 10.0  # m/s (high velocity)
    D_phys = 0.01  # m
    nu_water = 1.0e-6  # m²/s
    Re_phys = u_phys * D_phys / nu_water
    
    print(f"\nPhysical Reynolds: {Re_phys:.0f}")
    print(f"\nApproach 1: Conservative (Ma=0.1, tau=0.7)")
    
    scaling1 = DimensionlessScaling(
        Re_target=Re_phys,
        L_ref=D_phys,
        u_ref=u_phys,
        nu_ref=nu_water,
        Ma_target=0.1,
        tau_target=0.7
    )
    print(f"  Domain size: N = {scaling1.N} (very large!)")
    
    print(f"\nApproach 2: Aggressive (Ma=0.2, tau=0.6)")
    scaling2 = DimensionlessScaling(
        Re_target=Re_phys,
        L_ref=D_phys,
        u_ref=u_phys,
        nu_ref=nu_water,
        Ma_target=0.2,
        tau_target=0.6
    )
    print(f"  Domain size: N = {scaling2.N} (more practical)")
    print(f"  Warning: Higher Ma, lower tau → less stable")
    
    print(f"\nConclusion: For Re > 50,000, consider:")
    print(f"  1. Use larger Ma (up to 0.2) if stability allows")
    print(f"  2. Accept tau ≈ 0.6 (still acceptable)")
    print(f"  3. Or reduce physical Re (if possible)")
    print(f"  4. Or use turbulence models (LES, etc.)")
    
    return scaling1, scaling2


def create_comparison_plot(results_ma, results_tau):
    """Create visualization of scaling trade-offs."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Ma vs N
    ma_values = [r[0] for r in results_ma]
    N_values_ma = [r[1] for r in results_ma]
    
    ax1.plot(ma_values, N_values_ma, 'o-', linewidth=2, markersize=8, color='#2E86AB')
    ax1.axhline(y=1000, color='green', linestyle='--', alpha=0.5, label='Practical limit (~1000)')
    ax1.axhline(y=5000, color='orange', linestyle='--', alpha=0.5, label='Challenging (~5000)')
    ax1.set_xlabel('Mach Number (Ma)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Domain Size (N)', fontsize=12, fontweight='bold')
    ax1.set_title('Effect of Mach Number on Domain Size\n(Re=10,000, tau=0.7)', 
                  fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(bottom=0)
    
    # Plot 2: tau vs N
    tau_values = [r[0] for r in results_tau]
    N_values_tau = [r[1] for r in results_tau]
    
    ax2.plot(tau_values, N_values_tau, 's-', linewidth=2, markersize=8, color='#A23B72')
    ax2.axhline(y=1000, color='green', linestyle='--', alpha=0.5, label='Practical limit (~1000)')
    ax2.axhline(y=5000, color='orange', linestyle='--', alpha=0.5, label='Challenging (~5000)')
    ax2.axvline(x=0.6, color='red', linestyle='--', alpha=0.5, label='Stability threshold')
    ax2.set_xlabel('Relaxation Time (tau)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Domain Size (N)', fontsize=12, fontweight='bold')
    ax2.set_title('Effect of Relaxation Time on Domain Size\n(Re=10,000, Ma=0.1)', 
                  fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig('dimensionless_scaling_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: dimensionless_scaling_comparison.png")
    plt.close()


def practical_recommendations():
    """Print practical recommendations for users."""
    print("\n" + "="*70)
    print("PRACTICAL RECOMMENDATIONS")
    print("="*70)
    
    print("\n1. TARGET REYNOLDS NUMBER RANGES:")
    print("   Re < 1,000:      Easy - use conservative parameters")
    print("   1,000 < Re < 10,000:  Moderate - adjust Ma to 0.1-0.15")
    print("   10,000 < Re < 50,000: Challenging - use Ma=0.15-0.2, tau=0.6-0.65")
    print("   Re > 50,000:     Very difficult - may need special techniques")
    
    print("\n2. PARAMETER SELECTION:")
    print("   Mach Number (Ma):")
    print("     • Conservative: 0.05-0.1 (very stable, larger domains)")
    print("     • Moderate: 0.1-0.15 (balanced)")
    print("     • Aggressive: 0.15-0.2 (smaller domains, less stable)")
    print("     • Limit: < 0.3 (compressibility effects above this)")
    
    print("\n   Relaxation Time (tau):")
    print("     • Safe: 0.7-1.0 (very stable, larger domains)")
    print("     • Acceptable: 0.6-0.7 (stable, moderate domains)")
    print("     • Marginal: 0.55-0.6 (usable but watch for instabilities)")
    print("     • Limit: > 0.5 (numerical instability below this)")
    
    print("\n3. WORKFLOW:")
    print("   Step 1: Calculate physical Re = u*L/ν")
    print("   Step 2: Choose Ma target (start with 0.1)")
    print("   Step 3: Choose tau target (start with 0.7)")
    print("   Step 4: Use DimensionlessScaling to get N, dx, dt")
    print("   Step 5: Check if N is practical for your resources")
    print("   Step 6: If N too large, increase Ma or decrease tau")
    print("   Step 7: Validate simulation stability")
    
    print("\n4. DOMAIN SIZE GUIDELINES:")
    print("   N < 100:     Very coarse - only for testing")
    print("   100 < N < 1000:   Practical - good resolution")
    print("   1000 < N < 5000:  Large - requires significant resources")
    print("   N > 5000:    Very large - may need HPC or adjust parameters")
    
    print("\n5. EXAMPLE USE CASES:")
    print("   • Pipe flow Re=1000:   N~200, Ma=0.1, tau=0.7 ✓")
    print("   • Airfoil Re=10,000:   N~1000, Ma=0.15, tau=0.65 ✓")
    print("   • Car Re=1,000,000:    Not feasible with standard LBM")
    print("                          (use LES, DES, or wall models)")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("DIMENSIONLESS SCALING FOR HIGH REYNOLDS NUMBER LBM")
    print("="*70)
    print("\nThis example demonstrates proper unit scaling for LBM simulations")
    print("to achieve high Reynolds numbers while maintaining stability.")
    
    # Run examples
    scaling1 = example_moderate_reynolds()
    results_ma = example_high_reynolds_adjust_velocity()
    results_tau = example_high_reynolds_adjust_tau()
    scaling_high1, scaling_high2 = example_very_high_reynolds()
    
    # Create comparison plots
    create_comparison_plot(results_ma, results_tau)
    
    # Print recommendations
    practical_recommendations()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nKey takeaways:")
    print("1. Reynolds number determines domain size through: N = Re * ν_lattice / u_lattice")
    print("2. Mach number (Ma) controls u_lattice: u_lattice = Ma * c_s")
    print("3. Relaxation time (tau) controls ν_lattice: ν_lattice = (tau - 0.5)/3")
    print("4. Trade-off: Higher Ma or lower tau → smaller domain, less stable")
    print("5. For high Re, carefully balance Ma and tau to get practical domain sizes")
    print("\nUse the DimensionlessScaling class to automatically calculate parameters!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
