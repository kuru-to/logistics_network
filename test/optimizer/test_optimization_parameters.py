from src.utils.config_util import test_section
from src.optimizer.optimization_parameters import OptimizationParameters


def test_import_():
    test_parameter = OptimizationParameters.import_(test_section)

    assert test_parameter.NUM_THREADS == 1
