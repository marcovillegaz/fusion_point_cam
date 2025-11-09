"""
Test Suite for Component Class
File: tests/test_component.py

Focused tests for the Component dataclass

Run with: pytest tests/test_component.py -v
"""

# from dataclasses import FrozenInstanceError
import pytest

# Import Component class
from des_sle.data.component import Component


# =============================================================================
# FIXTURES


@pytest.fixture
def valid_component_data():
    """Valid component data for testing"""
    return {
        "name": "Choline Chloride",
        "Tm": 575.15,
        "dHfus": 4100,
        "MW": 139.62,
        "formula": "C5H14ClNO",
    }


@pytest.fixture
def minimal_component_data():
    """Minimal valid component data"""
    return {
        "name": "Test Component",
        "Tm": 300.0,
        "dHfus": 1000.0,
    }


# =============================================================================


# TEST COMPONENT CREATION
class TestComponentCreation:
    """Test various ways to create Component instances"""

    def test_create_with_all_fields(self, valid_component_data):
        """Test creating component with all fields"""

        comp = Component(**valid_component_data)

        assert comp.name == "Choline Chloride"
        assert comp.Tm == 575.15
        assert comp.dHfus == 4100
        assert comp.MW == 139.62
        assert comp.formula == "C5H14ClNO"

    def test_create_with_minimal_fields(self, minimal_component_data):
        """Test creating component with only required fields"""

        comp = Component(**minimal_component_data)

        assert comp.name == "Test Component"
        assert comp.Tm == 300.0
        assert comp.dHfus == 1000.0
        assert comp.MW is None
        assert comp.formula is None

    def test_create_with_positional_args(self):
        """Test creating component with positional arguments"""

        comp = Component("Water", 273.15, 6010)

        assert comp.name == "Water"
        assert comp.Tm == 273.15
        assert comp.dHfus == 6010

    def test_create_with_mixed_args(self):
        """Test creating component with mixed positional and keyword args"""

        comp = Component("Urea", 405.65, dHfus=14600, MW=60.06)

        assert comp.name == "Urea"
        assert comp.Tm == 405.65
        assert comp.dHfus == 14600
        assert comp.MW == 60.06


# TEST COMPONENT VALIDATION
class TestComponentValidation:
    """Test component data validation"""

    def test_negative_melting_temperature(self):
        """Test that negative Tm raises ValueError"""

        with pytest.raises(ValueError, match="Melting temperature must be positive"):
            Component("Invalid", Tm=-100, dHfus=1000)

    def test_zero_melting_temperature(self):
        """Test that zero Tm raises ValueError"""

        with pytest.raises(ValueError, match="Melting temperature must be positive"):
            Component("Invalid", Tm=0, dHfus=1000)

    def test_negative_enthalpy_fusion(self):
        """Test that negative ΔHfus raises ValueError"""

        with pytest.raises(ValueError, match="Enthalpy of fusion must be positive"):
            Component("Invalid", Tm=300, dHfus=-1000)

    def test_zero_enthalpy_fusion(self):
        """Test that zero ΔHfus raises ValueError"""

        with pytest.raises(ValueError, match="Enthalpy of fusion must be positive"):
            Component("Invalid", Tm=300, dHfus=0)

    def test_very_small_positive_values_accepted(self):
        """Test that very small positive values are accepted"""

        comp = Component("Helium", Tm=0.001, dHfus=0.001)

        assert comp.Tm == 0.001
        assert comp.dHfus == 0.001

    def test_very_large_values_accepted(self):
        """Test that very large values are accepted"""

        comp = Component("Tungsten", Tm=3695.0, dHfus=35400.0)

        assert comp.Tm == 3695.0
        assert comp.dHfus == 35400.0


# TEST COMPONENT PROPERTIES
class TestComponentProperties:
    """Test component properties and attributes"""

    def test_string_representation(self, valid_component_data):
        """Test __repr__ method"""

        comp = Component(**valid_component_data)
        repr_str = repr(comp)

        assert "Component" in repr_str
        assert "Choline Chloride" in repr_str
        assert "575.15" in repr_str
        assert "4100" in repr_str

    def test_optional_fields_default_to_none(self):
        """Test that optional fields default to None"""

        comp = Component("Simple", Tm=300, dHfus=1000)

        assert comp.MW is None
        assert comp.formula is None

    def test_all_attributes_accessible(self, valid_component_data):
        """Test that all attributes can be accessed"""

        comp = Component(**valid_component_data)

        # Should not raise any AttributeError
        _ = comp.name
        _ = comp.Tm
        _ = comp.dHfus
        _ = comp.MW
        _ = comp.formula


# TEST COMPONENT EQUALITY AND COMPARISON
class TestComponentComparison:
    """Test component equality and comparison"""

    def test_equality_same_data(self):
        """Test that components with same data are equal"""

        comp1 = Component("Water", 273.15, 6010)
        comp2 = Component("Water", 273.15, 6010)

        assert comp1 == comp2

    def test_inequality_different_name(self):
        """Test that components with different names are not equal"""

        comp1 = Component("Water", 273.15, 6010)
        comp2 = Component("Ice", 273.15, 6010)

        assert comp1 != comp2

    def test_inequality_different_tm(self):
        """Test that components with different Tm are not equal"""

        comp1 = Component("Water", 273.15, 6010)
        comp2 = Component("Water", 273.16, 6010)

        assert comp1 != comp2

    def test_inequality_different_dhfus(self):
        """Test that components with different ΔHfus are not equal"""

        comp1 = Component("Water", 273.15, 6010)
        comp2 = Component("Water", 273.15, 6020)

        assert comp1 != comp2


# TEST COMPONENT USE CASES
class TestComponentUseCases:
    """Test realistic use cases for Component class"""

    def test_common_des_components(self):
        """Test creating common DES components"""

        # Choline chloride
        chcl = Component(name="Choline Chloride", Tm=575.15, dHfus=4100, MW=139.62)

        # Urea
        urea = Component(name="Urea", Tm=405.65, dHfus=14600, MW=60.06)

        # Glycerol
        glycerol = Component(name="Glycerol", Tm=291.15, dHfus=18300, MW=92.09)

        # Ethylene glycol
        eg = Component(name="Ethylene Glycol", Tm=260.15, dHfus=9960, MW=62.07)

        components = [chcl, urea, glycerol, eg]

        # All should be valid
        assert len(components) == 4
        assert all(c.Tm > 0 for c in components)
        assert all(c.dHfus > 0 for c in components)

    def test_component_in_collection(self):
        """Test using components in a list/collection"""

        components = [
            Component("A", 300, 1000),
            Component("B", 400, 2000),
            Component("C", 500, 3000),
        ]

        # Test that we can iterate and access
        for comp in components:
            assert comp.Tm > 0

        # Test that we can sort by melting temperature
        sorted_comps = sorted(components, key=lambda c: c.Tm)
        assert sorted_comps[0].name == "A"
        assert sorted_comps[-1].name == "C"

    def test_component_as_dict_value(self):
        """Test using components as dictionary values"""

        database = {
            "chcl": Component("Choline Chloride", 575.15, 4100),
            "urea": Component("Urea", 405.65, 14600),
        }

        assert "chcl" in database
        assert database["chcl"].Tm == 575.15
        assert database["urea"].name == "Urea"


# TEST EDGE CASES
class TestComponentEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_unicode_in_name(self):
        """Test that unicode characters work in component name"""

        comp = Component("α-Naphthol", 300, 1000)
        assert "α" in comp.name

        comp2 = Component("水 (Water)", 273.15, 6010)
        assert "水" in comp2.name

    def test_very_long_name(self):
        """Test component with very long name"""

        long_name = "A" * 1000
        comp = Component(long_name, 300, 1000)

        assert comp.name == long_name
        assert len(comp.name) == 1000

    def test_empty_string_name(self):
        """Test component with empty string name (should be allowed)"""

        comp = Component("", 300, 1000)
        assert comp.name == ""

    def test_scientific_notation_values(self):
        """Test using scientific notation for values"""

        comp = Component("Test", Tm=3e2, dHfus=1e4)

        assert comp.Tm == 300.0
        assert comp.dHfus == 10000.0

    def test_float_precision(self):
        """Test that float precision is maintained"""

        comp = Component("Test", Tm=273.150001, dHfus=6010.99999)

        assert comp.Tm == 273.150001
        assert comp.dHfus == 6010.99999


# PARAMETRIZED TESTS
class TestComponentParametrized:
    """Parametrized tests for comprehensive coverage"""

    @pytest.mark.parametrize(
        "tm,dhfus",
        [
            (273.15, 6010),  # Water
            (575.15, 4100),  # Choline Chloride
            (405.65, 14600),  # Urea
            (291.15, 18300),  # Glycerol
            (3695, 35400),  # Tungsten
            (0.95, 59),  # Helium
        ],
    )
    def test_various_valid_components(self, tm, dhfus):
        """Test creating components with various valid property values"""

        comp = Component("Test", Tm=tm, dHfus=dhfus)

        assert comp.Tm == tm
        assert comp.dHfus == dhfus

    @pytest.mark.parametrize("invalid_tm", [-100, -1, 0, -273.15])
    def test_invalid_melting_temperatures(self, invalid_tm):
        """Test that various invalid Tm values raise errors"""

        with pytest.raises(ValueError):
            Component("Invalid", Tm=invalid_tm, dHfus=1000)

    @pytest.mark.parametrize("invalid_dhfus", [-1000, -1, 0, -0.001])
    def test_invalid_enthalpies(self, invalid_dhfus):
        """Test that various invalid ΔHfus values raise errors"""

        with pytest.raises(ValueError):
            Component("Invalid", Tm=300, dHfus=invalid_dhfus)


# RUN TESTS
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
