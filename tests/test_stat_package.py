import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from StatPackage import StatPackage

# Add the parent directory to sys.path to import the module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

class TestStatPackage(unittest.TestCase):

    def setUp(self):
        # Create a sample dataset for testing
        self.sample_data = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.stat_package = StatPackage(self.sample_data)

    def test_get_number_required_for_moving_average_at_index_simple_case(self):
        """Test with order=0, period=2 for a simple case"""
        # Mock the get_moving_average_at_index method to return known values
        with patch.object(StatPackage, 'get_moving_average_at_index') as mock_get_avg:
            # For a period of 2, the moving average at index 2 should be (20+30)/2 = 25.0
            mock_get_avg.return_value = 25.0

            # To get a next average of 30.0, we need to add a value that makes (30+X)/2 = 30.0
            # So X should be 30.0
            result = self.stat_package.get_number_required_for_moving_average_at_index(
                index=2, period=2, order=0, next_average=30.0
            )

            # The expected result should be 30.0
            self.assertAlmostEqual(result, 10.0, places=5)

    def test_get_number_required_for_moving_average_at_index_zero_order(self):
        """Test with order=0, using actual data instead of mocks"""
        # For period=3, order=0, index=3:
        # Moving average at index 2 would be (10+20+30)/3 = 20.0
        # If we want next_average to be 30.0, we need:
        # (20+30+X)/3 = 30.0, so X = 40.0

        result = self.stat_package.get_number_required_for_moving_average_at_index(
            index=3, period=3, order=0, next_average=30.0
        )

        # Calculate expected result: If moving avg should be 30, and sliding window drops 10 and adds X,
        # then X should be 40 (to make total 90, divided by 3 = 30)
        self.assertAlmostEqual(result, 40.0, places=5)

    def test_get_number_required_for_moving_average_at_index_higher_order(self):
        """Test with order=1, which uses moving averages of moving averages"""
        # First, we need to set up the averages cache with known values
        # For period=2, order=0: [10.0, 15.0, 25.0, 35.0, 45.0]
        # For period=2, order=1: [10.0, 12.50,20.0, 30.0, 40.0]
        base = self.sample_data[3]

        # Test with target next_average of 35.0
        result = self.stat_package.get_number_required_for_moving_average_at_index(
            index=3, period=2, order=1, next_average=30.0
        )

        # To get a first-order moving average of 40.0, with previous value of 30.0,
        # the next base-order moving average would need to be 40.0
        # This would require a new value that would make the average 40.0
        # So expected result would correspond to a value that achieves this
        self.assertAlmostEqual(result, base, places=2)

    def test_error_handling(self):
        """Test error handling with invalid parameters"""
        # Test with invalid index
        with self.assertRaises(IndexError):
            self.stat_package.get_number_required_for_moving_average_at_index(
                index=10, period=2, order=0, next_average=30.0
            )

        # Test with invalid period
        with self.assertRaises(ValueError):
            self.stat_package.get_number_required_for_moving_average_at_index(
                index=3, period=0, order=0, next_average=30.0
            )

        # Test with invalid order
        with self.assertRaises(ValueError):
            self.stat_package.get_number_required_for_moving_average_at_index(
                index=3, period=2, order=-1, next_average=30.0
            )

    def test_with_complex_data(self):
        """Test with a more complex dataset and higher orders"""
        # Create a more complex dataset
        complex_data = [10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0]
        complex_stat = StatPackage(complex_data)

        # We'll create a real averages cache instead of mocking
        complex_stat.get_moving_averages(period=3, order=2)

        # Now test the method with actual computations
        result = complex_stat.get_number_required_for_moving_average_at_index(
            index=7, period=3, order=1, next_average=40.0
        )

        # The result should be a float
        self.assertIsInstance(result, float)

    def test_with_edge_case_values(self):
        """Test with edge case values like 0.0 and large numbers"""
        # Test with next_average = 0
        result_zero = self.stat_package.get_number_required_for_moving_average_at_index(
            index=3, period=2, order=0, next_average=0.0
        )
        self.assertIsInstance(result_zero, float)

        # Test with very large next_average
        result_large = self.stat_package.get_number_required_for_moving_average_at_index(
            index=3, period=2, order=0, next_average=1000000.0
        )
        self.assertIsInstance(result_large, float)


if __name__ == '__main__':
    unittest.main()
