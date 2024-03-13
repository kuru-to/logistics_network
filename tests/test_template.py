""""Test template"""
import pytest


class TestTemplate:
    @pytest.fixture()
    def setUp(self):
        pass

    @pytest.mark.slow
    def test_aaa(self, setUp):
        """処理に時間がかかるテストには `pyters.mark.slow` をつける"""
        assert 1 == 1
