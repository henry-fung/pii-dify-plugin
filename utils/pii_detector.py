from typing import Dict, List, Any, Optional
import json
import re


class PIIDetector:
    """PII检测核心类"""

    def __init__(self):
        with open('pii_prompt.md', 'r', encoding='utf-8') as f:
            task_prompt = f.read()
        self.task_prompt = task_prompt
        self.input_prompt = '''# 输入
給定的文字是:
```text
{text}
```'''

    def generate_detection_prompt(self, text: str) -> str:
        """
        生成PII检测的prompt
        
        Args:
            text: 待检测的文本
            categories: 要检测的PII类别列表，None表示检测所有类别
            
        Returns:
            用于LLM的检测prompt
        """

        prompt = self.task_prompt+self.input_prompt.format(text=text)


        return prompt

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM返回的JSON响应
        
        Args:
            response: LLM的响应文本
            
        Returns:
            解析后的字典，如果解析失败返回错误信息
        """
        try:
            # 尝试直接解析JSON
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # 如果都失败了，返回错误信息
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response
            }

    # def validate_detection_result(self, result: Dict[str, Any]) -> bool:
    #     """
    #     验证检测结果的格式是否正确
    #
    #     Args:
    #         result: 检测结果字典
    #
    #     Returns:
    #         是否为有效格式
    #     """
    #     required_fields = ['has_pii', 'detected_items', 'risk_level', 'summary']
    #     return all(field in result for field in required_fields)


# 创建全局实例
pii_detector = PIIDetector()
