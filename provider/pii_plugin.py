from collections.abc import Mapping
from typing import Any

try:
    from dify_plugin.entities.model import ModelType
    from dify_plugin import ToolProvider
except ImportError:
    # 在开发环境中可能无法导入，定义占位符类
    class ToolProvider:
        pass


class PiiPluginProvider(ToolProvider):
    def _validate_credentials(self, credentials: Mapping[str, Any]) -> None:
        """
        验证凭证配置
        由于此插件使用 Dify 内置的 LLM，暂时不需要额外的凭证验证
        """
        pass