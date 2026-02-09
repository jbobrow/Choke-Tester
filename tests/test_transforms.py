"""
Tests for the 3MF transform parser.
"""

import numpy as np
import pytest

from integrations.transforms import parse_transform


class TestParseTransform:
    def test_none_returns_identity(self):
        result = parse_transform(None)
        np.testing.assert_array_equal(result, np.eye(4))

    def test_empty_string_returns_identity(self):
        result = parse_transform("")
        np.testing.assert_array_equal(result, np.eye(4))

    def test_whitespace_returns_identity(self):
        result = parse_transform("   ")
        np.testing.assert_array_equal(result, np.eye(4))

    def test_identity_12_values(self):
        s = "1 0 0 0  0 1 0 0  0 0 1 0"
        result = parse_transform(s)
        np.testing.assert_allclose(result, np.eye(4), atol=1e-12)

    def test_translation(self):
        # Translation by (10, 20, 30)
        s = "1 0 0 10  0 1 0 20  0 0 1 30"
        result = parse_transform(s)
        assert result[0, 3] == 10.0
        assert result[1, 3] == 20.0
        assert result[2, 3] == 30.0

    def test_16_values(self):
        s = "1 0 0 5  0 1 0 10  0 0 1 15  0 0 0 1"
        result = parse_transform(s)
        assert result.shape == (4, 4)
        assert result[3, 3] == 1.0

    def test_invalid_count_raises(self):
        with pytest.raises(ValueError, match="Expected 12 or 16"):
            parse_transform("1 2 3 4 5")
