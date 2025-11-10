"""
Test Suite for Deep Eutectic Solvent SLE Modeling
File: tests/test_nrtl.py

Run with: pytest tests/test_nrtl.py -v
"""

import pytest
import numpy as np
from numpy.testing import assert_allclose, assert_array_less

# Import from your source code (adjust path as needed)
# Assuming structure: src/des_sle/...
# For now, we'll assume the classes are importable as shown below
from des_sle.models.nrtl import NRTL
from des_sle.data.component import Component


# =============================================================================
# FIXTURES - Shared test data
@pytest.fixture
def nrtl_model():
    """Provide a fresh NRTL model instance"""

    return NRTL()


@pytest.fixture
def ethanol_water_params():
    """NRTL parameters for ethanol-water system (literature values)"""
    return {"tau12": 0.5273, "tau21": -0.1706, "alpha12": 0.3037}


@pytest.fixture
def symmetric_params():
    """Symmetric parameters for ideal solution testing"""
    return {"tau12": 0.0, "tau21": 0.0, "alpha12": 0.3}


@pytest.fixture
def chcl_urea_components():
    """Choline Chloride - Urea DES system components"""

    chcl = Component(name="Choline Chloride", Tm=575.15, dHfus=4100, MW=139.62, formula="C5H14ClNO")

    urea = Component(name="Urea", Tm=405.65, dHfus=14600, MW=60.06, formula="CH4N2O")

    return [chcl, urea]


# TEST COMPONENT CLASS (THIS SHOULD BE IN test_components.py)
class TestComponent:
    """Test suite for Component class"""

    def test_component_creation(self, chcl_urea_components):
        """Test basic component creation"""
        chcl, urea = chcl_urea_components

        assert chcl.name == "Choline Chloride"
        assert chcl.Tm == 575.15
        assert chcl.dHfus == 4100
        assert chcl.MW == 139.62

    def test_component_repr(self, chcl_urea_components):
        """Test component string representation"""
        chcl = chcl_urea_components[0]
        repr_str = repr(chcl)

        assert "Choline Chloride" in repr_str
        assert "575.15" in repr_str
        assert "4100" in repr_str

    def test_negative_melting_temperature(self):
        """Test that negative Tm raises ValueError"""

        with pytest.raises(ValueError, match="Melting temperature must be positive"):
            Component("Invalid", Tm=-100, dHfus=1000)

    def test_negative_enthalpy(self):
        """Test that negative ΔHfus raises ValueError"""

        with pytest.raises(ValueError, match="Enthalpy of fusion must be positive"):
            Component("Invalid", Tm=300, dHfus=-1000)

    def test_zero_values(self):
        """Test that zero Tm or ΔHfus raises ValueError"""

        with pytest.raises(ValueError):
            Component("Invalid", Tm=0, dHfus=1000)

        with pytest.raises(ValueError):
            Component("Invalid", Tm=300, dHfus=0)

    def test_optional_fields(self):
        """Test component with minimal required fields"""

        comp = Component("Simple", Tm=300, dHfus=1000)

        assert comp.name == "Simple"
        assert comp.MW is None
        assert comp.formula is None


# TEST NRTL BASIC FUNCTIONALITY
class TestNRTLBasic:
    """Test basic NRTL functionality"""

    def test_nrtl_initialization(self, nrtl_model):
        """Test NRTL model initialization"""
        assert nrtl_model.name == "NRTL"

    def test_parameter_names_binary(self, nrtl_model):
        """Test parameter name generation for binary system"""
        params = nrtl_model.get_parameter_names(2)

        assert "tau12" in params
        assert "tau21" in params
        assert "alpha12" in params
        assert "alpha21" in params

    def test_parameter_names_ternary(self, nrtl_model):
        """Test parameter name generation for ternary system"""
        params = nrtl_model.get_parameter_names(3)

        # Should have 6 tau parameters (3*2)
        tau_params = [p for p in params if p.startswith("tau")]
        assert len(tau_params) == 6

        # Should have 6 alpha parameters
        alpha_params = [p for p in params if p.startswith("alpha")]
        assert len(alpha_params) == 6

    def test_activity_coefficient_returns_array(self, nrtl_model, ethanol_water_params):
        """Test that activity_coefficient returns numpy array"""
        gamma = nrtl_model.activity_coefficient([0.5, 0.5], 298.15, ethanol_water_params)

        assert isinstance(gamma, np.ndarray)
        assert len(gamma) == 2

    def test_activity_coefficients_positive(self, nrtl_model, ethanol_water_params):
        """Test that activity coefficients are always positive"""
        compositions = [[0.1, 0.9], [0.5, 0.5], [0.9, 0.1]]

        for x in compositions:
            gamma = nrtl_model.activity_coefficient(x, 298.15, ethanol_water_params)
            assert np.all(gamma > 0), f"Activity coefficients must be positive, got {gamma}"


# TEST NRTL COMPOSITION VALIDATION
class TestNRTLValidation:
    """Test NRTL input validation"""

    def test_composition_sum_not_one(self, nrtl_model, symmetric_params):
        """Test that composition not summing to 1 raises error"""
        with pytest.raises(ValueError, match="sum to 1.0"):
            nrtl_model.activity_coefficient([0.5, 0.6], 298.15, symmetric_params)

    def test_negative_composition(self, nrtl_model, symmetric_params):
        """Test that negative composition raises error"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            nrtl_model.activity_coefficient([-0.1, 1.1], 298.15, symmetric_params)

    def test_composition_greater_than_one(self, nrtl_model, symmetric_params):
        """Test that composition > 1 raises error"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            nrtl_model.activity_coefficient([1.5, -0.5], 298.15, symmetric_params)

    def test_missing_tau12_parameter(self, nrtl_model):
        """Test that missing tau12 raises KeyError"""
        incomplete_params = {"tau21": -0.2, "alpha12": 0.3}

        with pytest.raises(KeyError):
            nrtl_model.activity_coefficient([0.5, 0.5], 298.15, incomplete_params)

    def test_missing_tau21_parameter(self, nrtl_model):
        """Test that missing tau21 raises KeyError"""
        incomplete_params = {"tau12": 0.5, "alpha12": 0.3}

        with pytest.raises(KeyError):
            nrtl_model.activity_coefficient([0.5, 0.5], 298.15, incomplete_params)


# TEST NRTL THERMODYNAMIC CONSISTENCY
class TestNRTLThermodynamics:
    """Test thermodynamic consistency of NRTL model"""

    def test_ideal_solution_limit(self, nrtl_model, symmetric_params):
        """Test that tau=0 gives gamma=1 (ideal solution)"""
        gamma = nrtl_model.activity_coefficient([0.5, 0.5], 298.15, symmetric_params)

        assert_allclose(
            gamma, [1.0, 1.0], atol=1e-10, err_msg="Zero tau parameters should give ideal solution"
        )

    def test_ideal_solution_various_compositions(self, nrtl_model, symmetric_params):
        """Test ideal solution at multiple compositions"""
        compositions = [[0.1, 0.9], [0.3, 0.7], [0.7, 0.3], [0.9, 0.1]]

        for x in compositions:
            gamma = nrtl_model.activity_coefficient(x, 298.15, symmetric_params)
            assert_allclose(gamma, [1.0, 1.0], atol=1e-10, err_msg=f"Failed at composition {x}")

    def test_pure_component_limit(self, nrtl_model, ethanol_water_params):
        """Test that gamma → 1 as xi → 1 (pure component limit)"""
        # Component 1 approaching pure
        gamma = nrtl_model.activity_coefficient([0.9999, 0.0001], 298.15, ethanol_water_params)
        assert abs(gamma[0] - 1.0) < 0.01, "Pure component should have gamma ≈ 1"

        # Component 2 approaching pure
        gamma = nrtl_model.activity_coefficient([0.0001, 0.9999], 298.15, ethanol_water_params)
        assert abs(gamma[1] - 1.0) < 0.01, "Pure component should have gamma ≈ 1"

    def test_infinite_dilution_higher_than_finite(self, nrtl_model):
        """Test that infinite dilution gamma > finite concentration gamma (for positive tau)"""
        params = {"tau12": 0.5, "tau21": 0.5, "alpha12": 0.3}

        # Infinite dilution (approximate)
        gamma_inf = nrtl_model.activity_coefficient([0.001, 0.999], 298.15, params)

        # Finite concentration
        gamma_finite = nrtl_model.activity_coefficient([0.5, 0.5], 298.15, params)

        # For positive tau, dilute component should have higher gamma
        assert gamma_inf[0] > gamma_finite[0]

    def test_gibbs_duhem_smoothness(self, nrtl_model, ethanol_water_params):
        """Test that activity coefficients change smoothly (Gibbs-Duhem related)"""
        x1 = np.array([0.5, 0.5])
        x2 = np.array([0.501, 0.499])

        gamma1 = nrtl_model.activity_coefficient(x1, 298.15, ethanol_water_params)
        gamma2 = nrtl_model.activity_coefficient(x2, 298.15, ethanol_water_params)

        # Small composition change should give small gamma change
        assert abs(gamma1[0] - gamma2[0]) < 0.01
        assert abs(gamma1[1] - gamma2[1]) < 0.01


# TEST NRTL WITH DIFFERENT PARAMETER SETS
class TestNRTLParameterSets:
    """Test NRTL with various parameter combinations"""

    @pytest.mark.parametrize("alpha", [0.2, 0.3, 0.4, 0.47])
    def test_different_alpha_values(self, nrtl_model, alpha):
        """Test NRTL with different alpha parameters"""
        params = {"tau12": 0.5, "tau21": -0.2, "alpha12": alpha}

        gamma = nrtl_model.activity_coefficient([0.5, 0.5], 298.15, params)

        assert len(gamma) == 2
        assert np.all(gamma > 0)

    @pytest.mark.parametrize(
        "tau12,tau21",
        [
            (0.5, 0.5),  # Symmetric positive
            (-0.5, -0.5),  # Symmetric negative
            (1.0, -1.0),  # Asymmetric
            (2.0, -0.5),  # Large asymmetry
        ],
    )
    def test_different_tau_combinations(self, nrtl_model, tau12, tau21):
        """Test NRTL with different tau parameter combinations"""
        params = {"tau12": tau12, "tau21": tau21, "alpha12": 0.3}

        gamma = nrtl_model.activity_coefficient([0.5, 0.5], 298.15, params)

        assert len(gamma) == 2
        assert np.all(gamma > 0)

    def test_default_alpha_parameter(self, nrtl_model):
        """Test that alpha defaults to 0.3 when not provided"""
        params_no_alpha = {"tau12": 0.5, "tau21": -0.2}
        params_with_alpha = {"tau12": 0.5, "tau21": -0.2, "alpha12": 0.3}

        gamma1 = nrtl_model.activity_coefficient([0.5, 0.5], 298.15, params_no_alpha)
        gamma2 = nrtl_model.activity_coefficient([0.5, 0.5], 298.15, params_with_alpha)

        assert_allclose(gamma1, gamma2, rtol=1e-10)


# TEST NRTL COMPOSITION RANGE
class TestNRTLCompositionRange:
    """Test NRTL across full composition range"""

    def test_composition_sweep(self, nrtl_model, ethanol_water_params):
        """Test activity coefficients across full composition range"""
        x1_range = np.linspace(0.01, 0.99, 20)

        for x1 in x1_range:
            x = [x1, 1 - x1]
            gamma = nrtl_model.activity_coefficient(x, 298.15, ethanol_water_params)

            assert len(gamma) == 2
            assert np.all(gamma > 0)
            assert np.all(np.isfinite(gamma)), f"Non-finite gamma at x1={x1}"

    def test_equimolar_composition(self, nrtl_model, ethanol_water_params):
        """Test activity coefficient at equimolar composition"""
        gamma = nrtl_model.activity_coefficient([0.5, 0.5], 298.15, ethanol_water_params)

        # For ethanol-water with these parameters, expect positive deviation
        assert gamma[0] > 1.0
        assert gamma[1] > 1.0

    def test_boundary_compositions(self, nrtl_model, ethanol_water_params):
        """Test near-boundary compositions"""
        # Near x1 = 0
        gamma = nrtl_model.activity_coefficient([0.01, 0.99], 298.15, ethanol_water_params)
        assert np.all(np.isfinite(gamma))

        # Near x1 = 1
        gamma = nrtl_model.activity_coefficient([0.99, 0.01], 298.15, ethanol_water_params)
        assert np.all(np.isfinite(gamma))


# INTEGRATION TESTS
class TestNRTLIntegration:
    """Integration tests combining multiple components"""

    def test_complete_calculation_workflow(
        self, nrtl_model, chcl_urea_components, ethanol_water_params
    ):
        """Test complete workflow: components + NRTL calculation"""
        chcl, urea = chcl_urea_components

        # Verify components are valid
        assert chcl.Tm > 0
        assert urea.Tm > 0

        # Calculate activity coefficients at eutectic composition (approximately)
        x_eutectic = [0.33, 0.67]  # ChCl:Urea ≈ 1:2 molar

        gamma = nrtl_model.activity_coefficient(x_eutectic, 298.15, ethanol_water_params)

        assert len(gamma) == 2
        assert np.all(gamma > 0)

    def test_temperature_independence_basic_nrtl(self, nrtl_model, ethanol_water_params):
        """Test that basic NRTL (non-temperature-dependent) gives same result at different T"""
        x = [0.5, 0.5]

        gamma_298 = nrtl_model.activity_coefficient(x, 298.15, ethanol_water_params)
        gamma_350 = nrtl_model.activity_coefficient(x, 350.15, ethanol_water_params)

        # Basic NRTL doesn't depend on T (only on composition and parameters)
        # Note: In practice, parameters might be temperature-dependent
        assert_allclose(gamma_298, gamma_350, rtol=1e-10)


# PERFORMANCE TESTS
@pytest.mark.performance
class TestNRTLPerformance:
    """Performance-related tests (marked separately)"""

    def test_vectorized_calculation(self, nrtl_model, ethanol_water_params):
        """Test that multiple calculations complete quickly"""
        import time

        compositions = [[i / 100, 1 - i / 100] for i in range(1, 100)]

        start = time.time()
        for x in compositions:
            nrtl_model.activity_coefficient(x, 298.15, ethanol_water_params)
        elapsed = time.time() - start

        # 99 calculations should take less than 1 second
        assert elapsed < 1.0, f"Performance issue: {elapsed:.3f}s for 99 calculations"


# RUN TESTS
if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
