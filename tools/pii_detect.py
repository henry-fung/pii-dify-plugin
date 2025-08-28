from collections.abc import Generator
from typing import Any, Optional, List
import json

try:
    from dify_plugin import Tool
    from dify_plugin.entities.tool import ToolInvokeMessage
    from dify_plugin.entities.model.message import UserPromptMessage
except ImportError:
    # 在开发环境中可能无法导入，定义占位符类
    class Tool:
        pass
    class ToolInvokeMessage:
        pass
    class UserPromptMessage:
        pass

# 导入PII检测核心逻辑
from utils.pii_detector import pii_detector


class PiiDetectTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        检测文本中的PII信息
        """
        try:
            # 获取必需参数
            text = tool_parameters.get("text", "").strip()
            
            if not text:
                yield self.create_text_message("错误：请提供需要检测的文本内容。")
                return
            
            # 获取可选的PII类别参数
            pii_categories_str = tool_parameters.get("pii_categories")
            categories: Optional[List[str]] = None
            
            if pii_categories_str:
                # 解析逗号分隔的类别列表
                categories = [cat.strip() for cat in pii_categories_str.split(",") if cat.strip()]
                yield self.create_text_message(f"检测特定类别：{', '.join(categories)}")
            else:
                yield self.create_text_message("检测所有PII类别...")
            
            # 生成检测prompt
            detection_prompt = pii_detector.generate_detection_prompt(text, categories)
            
            # 获取模型配置
            model_config = tool_parameters.get("model")
            if not model_config:
                yield self.create_text_message("错误：请选择一个LLM模型。")
                return
            
            # 调用LLM进行检测
            llm_result = ""
            try:
                response = self.session.model.llm.invoke(
                    model_config=model_config,
                    prompt_messages=[
                        UserPromptMessage(content=detection_prompt)
                    ],
                    stream=False
                )
                
                if hasattr(response, 'message') and hasattr(response.message, 'content'):
                    llm_result = response.message.content
                elif hasattr(response, 'content'):
                    llm_result = response.content
                else:
                    llm_result = str(response)
                    
            except Exception as e:
                yield self.create_text_message(f"错误：LLM调用失败：{str(e)}")
                return
            
            if not llm_result:
                yield self.create_text_message("错误：LLM调用失败，无法进行PII检测。")
                return
            
            # 解析LLM响应
            detection_result = pii_detector.parse_json_response(llm_result)
            
            if "error" in detection_result:
                yield self.create_text_message(f"解析错误：{detection_result['error']}")
                yield self.create_text_message(f"原始响应：{detection_result.get('raw_response', 'N/A')}")
                return
            
            # 验证结果格式
            if not pii_detector.validate_detection_result(detection_result):
                yield self.create_text_message("警告：检测结果格式不完整，可能影响准确性。")
            
            # 生成检测摘要
            has_pii = detection_result.get("has_pii", False)
            risk_level = detection_result.get("risk_level", "unknown")
            detected_count = len(detection_result.get("detected_items", []))
            
            if has_pii:
                yield self.create_text_message(
                    f"✅ PII检测完成\n"
                    f"🔍 检测到 {detected_count} 个PII项目\n"
                    f"⚠️ 风险等级：{risk_level}\n"
                    f"📋 摘要：{detection_result.get('summary', '无摘要')}"
                )
                
                # 显示检测到的PII项目详情
                for i, item in enumerate(detection_result.get("detected_items", []), 1):
                    yield self.create_text_message(
                        f"🔸 项目 {i}：{item.get('category', 'unknown')}\n"
                        f"   值：{item.get('value', 'N/A')}\n"
                        f"   置信度：{item.get('confidence', 0):.2f}\n"
                        f"   位置：{item.get('start_pos', 0)}-{item.get('end_pos', 0)}\n"
                        f"   描述：{item.get('description', '无描述')}"
                    )
            else:
                yield self.create_text_message(
                    f"✅ PII检测完成\n"
                    f"🔍 未检测到PII信息\n"
                    f"📋 摘要：{detection_result.get('summary', '文本中未发现个人身份识别信息')}"
                )
            
            # 返回结构化结果用于工作流
            yield self.create_json_message(detection_result)
            yield self.create_variable_message("detection_result", detection_result)
            yield self.create_variable_message("has_pii", has_pii)
            yield self.create_variable_message("risk_level", risk_level)
            
        except Exception as e:
            yield self.create_text_message(f"PII检测过程中发生错误：{str(e)}")
    
