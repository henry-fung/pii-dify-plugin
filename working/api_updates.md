# API 更新记录

## 根据官方文档更新 LLM 调用方式

### 更新内容

1. **添加了 model-selector 参数**：
   - 所有三个工具都增加了 `model` 参数
   - 类型为 `model-selector`，作用域为 `llm`
   - 允许用户在 UI 中选择要使用的 LLM 模型

2. **更新了 LLM 调用API**：
   - 使用 `self.session.model.llm.invoke()` 替代旧的调用方式
   - 传入用户选择的 `model_config`
   - 使用 `UserPromptMessage` 构造消息

3. **按照官方最佳实践**：
   - 不再手动构建 LLMModelConfig
   - 让用户通过 UI 选择模型
   - 确保与 Dify 插件系统完全兼容

### 文件修改

- `tools/pii_detect.yaml` - 添加 model-selector 参数
- `tools/pii_detect.py` - 更新 LLM 调用方式
- `tools/pii_analyze.yaml` - 添加 model-selector 参数 
- `tools/pii_analyze.py` - 更新 LLM 调用方式
- `tools/pii_mask.yaml` - 添加 model-selector 参数
- `tools/pii_mask.py` - 更新 LLM 调用方式

### 使用方式

现在用户需要在使用任何 PII 工具时：
1. 提供待处理的文本
2. 选择要使用的 LLM 模型
3. 根据需要配置其他可选参数

这样确保了插件与 Dify 平台的完全兼容性，并遵循了官方推荐的最佳实践。