import logging
from composite.services.analysis.composite_service import CompositeService

def test_composite():
    """Test the Composite Service."""
    c = CompositeService()
    assert c is not None