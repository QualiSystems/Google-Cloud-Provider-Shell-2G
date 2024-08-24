import unittest

from src.driver import GoogleloudProviderShell2GDriver


class TestGoogleCloudProviderShell2GDriver(unittest.TestCase):
    def setUp(self):
        GoogleloudProviderShell2GDriver()

    def tearDown(self):
        pass

    def test_000_something(self):
        pass


if __name__ == "__main__":
    import sys

    sys.exit(unittest.main())
