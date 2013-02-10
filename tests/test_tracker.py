import unittest
from tracker.tracker import TrackerInflacion

class TestTracker(unittest.TestCase):

    def test_tracker(self):
    	tracker = TrackerInflacion(data_folder="tests/test-data/", product_file="test_products.csv", price_folder="0000-00/")
        a = tracker.get_prices()

if __name__ == '__main__':
    unittest.main()