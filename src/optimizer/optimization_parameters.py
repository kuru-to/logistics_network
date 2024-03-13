import pydantic

from ..utils import config_utils


@pydantic.dataclasses.dataclass
class OptimizationParameters:
    """最適化の計算に使用するパラメータをまとめた class

    Args:
        NUM_THREADS: 最適化実行時のスレッド数
        MAX_SECONDS: 最適化に使用可能な最大秒数
    """
    NUM_THREADS: int = 4
    MAX_SECONDS: int = 1800

    @classmethod
    def import_(cls, config_section: str) -> 'OptimizationParameters':
        config = config_utils.read_config(section=config_section)
        filename_config_opt = config.get("PATH_CONFIG") + config.get("CONFIG_OPTIMIZER")
        config_opt = config_utils.read_config(filename_config_opt, section=config_section)
        return cls(**config_opt)
