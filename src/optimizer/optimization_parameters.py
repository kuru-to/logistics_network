import pydantic

from ..utils.config_util import read_config


@pydantic.dataclasses.dataclass
class OptimizationParameters:
    """最適化の計算に使用するパラメータをまとめた class

    Args:
        NUM_THREADS: 最適化実行時のスレッド数
        MAX_SECONDS: 最適化に使用可能な最大秒数
    """
    NUM_THREADS: int
    MAX_SECONDS: int

    @classmethod
    def import_(cls, config_section: str) -> 'OptimizationParameters':
        config = read_config(section=config_section)
        filename_config_opt = config.get("PATH_CONFIG") + config.get("CONFIG_OPTIMIZER")
        config_opt = read_config(filename_config_opt, section=config_section)
        return cls(**config_opt)
