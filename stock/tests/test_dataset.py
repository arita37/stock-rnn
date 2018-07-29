import os
from unittest import TestCase

import numpy as np
import pandas as pd

from stock.dataset import StockData, StockDataSet
from stock.utils import get_path, recover_normalized_prices


class TestDataModel(TestCase):

    def setUp(self):
        super().setUp()

        # Generate test data.
        df = pd.read_csv(get_path("data/SP500.csv"))
        df['Close'] = list(range(1, df.shape[0] + 1))
        print(df.head())
        df.to_csv(get_path("data/_TEST_.csv"))

    def tearDown(self):
        super().tearDown()
        os.remove(get_path("data/_TEST_.csv"))

    def test_prepare_data(self):
        # Not normalized
        data = StockData(input_size=3, num_steps=5, stock_sym="_TEST_", normalized=False)
        assert np.array_equal(data.train_X[0], np.arange(1, 1 + 15).reshape((5, 3)))
        assert np.array_equal(data.train_X[1], np.arange(4, 4 + 15).reshape((5, 3)))
        assert np.array_equal(data.train_y[0], np.array([16, 17, 18]))
        assert np.array_equal(data.train_y[1], np.array([19, 20, 21]))

        # Normalized
        data = StockData(input_size=3, num_steps=5, stock_sym="_TEST_")
        assert np.array_equal(data.train_X[0][1], np.array([4, 5, 6]) / 3. - 1.0)
        assert np.array_equal(data.train_X[0][2], np.array([7, 8, 9]) / 6. - 1.0)
        assert np.array_equal(data.train_y[0], np.array([16, 17, 18]) / 15. - 1.0)

    def test_dataset(self):
        dataset = StockDataSet(['FB', 'GOOG'])
        for sym, batch_X, batch_y in dataset.generate_one_epoch(100):
            print(sym, batch_X.shape, batch_y.shape)

    def test_recover_normalized_prices(self):
        d1 = StockData(input_size=3, num_steps=5, stock_sym="_TEST_")
        d2 = StockData(input_size=3, num_steps=5, stock_sym="_TEST_", normalized=False)
        for i in range(5):
            init_denom = d2.train_X[i - 1][0][-1] if i > 0 else d2.train_X[i][0][0]
            recovered_prices = recover_normalized_prices(d1.train_X[i], init_denom)
            assert np.allclose(recovered_prices, d2.train_X[i])

    def test_random_stuff(self):
        d = StockDataSet(['_TEST_'], input_size=3, num_steps=5, normalized=False)
        print(d.test_X[:10])
        print(d.test_y[:10])