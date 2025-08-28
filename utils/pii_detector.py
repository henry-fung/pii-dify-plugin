from typing import Dict, List, Any, Optional
import json
import re


class PIIDetector:
    """PII检测核心类"""
    
    def __init__(self):
        self.pii_categories = {
            'person_name': '姓名/人名',
            'email': '电子邮件地址', 
            'phone': '电话号码',
            'id_number': '身份证号码',
            'address': '地址信息',
            'bank_account': '银行账号',
            'credit_card': '信用卡号',
            'passport': '护照号码',
            'driver_license': '驾照号码',
            'social_security': '社会保障号码',
            'date_of_birth': '出生日期',
            'organization': '组织/公司名称'
        }
    
    def generate_detection_prompt(self, text: str, categories: Optional[List[str]] = None) -> str:
        """
        生成PII检测的prompt
        
        Args:
            text: 待检测的文本
            categories: 要检测的PII类别列表，None表示检测所有类别
            
        Returns:
            用于LLM的检测prompt
        """
        if categories is None:
            categories = list(self.pii_categories.keys())
        
        category_desc = []
        for cat in categories:
            if cat in self.pii_categories:
                category_desc.append(f"- {cat}: {self.pii_categories[cat]}")
        
        prompt = f"""请分析以下文本中是否包含个人身份识别信息(PII)。

检测类别：
{chr(10).join(category_desc)}

待检测文本：
{text}

请按照以下JSON格式返回检测结果：
{{
    "has_pii": true/false,
    "detected_items": [
        {{
            "category": "PII类别",
            "value": "检测到的值",
            "confidence": 0.0-1.0,
            "start_pos": 开始位置,
            "end_pos": 结束位置,
            "description": "详细描述"
        }}
    ],
    "risk_level": "low/medium/high",
    "summary": "检测结果摘要"
}}

注意：
1. 只返回JSON格式的结果，不要包含其他文字
2. confidence表示检测置信度，范围0.0-1.0
3. 位置信息指在原文本中的字符位置
4. risk_level根据检测到的PII类型和数量评估风险等级"""
        
        return prompt
    
    def generate_analysis_prompt(self, text: str, detection_result: Dict[str, Any]) -> str:
        """
        生成PII分析的prompt
        
        Args:
            text: 原始文本
            detection_result: 检测结果
            
        Returns:
            用于LLM的分析prompt
        """
        prompt = f"""基于以下PII检测结果，对文本进行深入分析：

原始文本：
{text}

检测结果：
{json.dumps(detection_result, ensure_ascii=False, indent=2)}

请提供以下分析，以JSON格式返回：
{{
    "privacy_risk_assessment": {{
        "overall_risk": "low/medium/high/critical",
        "risk_factors": ["风险因素列表"],
        "recommendations": ["建议措施列表"]
    }},
    "compliance_analysis": {{
        "gdpr_relevant": true/false,
        "ccpa_relevant": true/false,
        "other_regulations": ["相关法规列表"],
        "compliance_notes": "合规性说明"
    }},
    "data_sensitivity": {{
        "sensitivity_level": "public/internal/confidential/restricted",
        "sensitive_combinations": ["敏感信息组合"],
        "context_analysis": "上下文分析"
    }},
    "remediation_suggestions": [
        {{
            "action": "建议行动",
            "priority": "high/medium/low",
            "description": "详细说明"
        }}
    ]
}}

只返回JSON格式的结果。"""
        
        return prompt
    
    def generate_masking_prompt(self, text: str, mask_strategy: str = "partial") -> str:
        """
        生成PII脱敏的prompt
        
        Args:
            text: 待脱敏的文本
            mask_strategy: 脱敏策略 (partial/full/replacement)
            
        Returns:
            用于LLM的脱敏prompt
        """
        strategy_descriptions = {
            "partial": "部分遮掩，保留部分字符用于识别",
            "full": "完全遮掩，使用***替换",
            "replacement": "使用虚假但格式正确的数据替换"
        }
        
        prompt = f"""请对以下文本中的PII信息进行脱敏处理。

脱敏策略：{mask_strategy} - {strategy_descriptions.get(mask_strategy, "部分遮掩")}

原始文本：
{text}

脱敏规则：
1. 姓名：保留姓氏，名字用*替换，如"张*"
2. 电话：保留前3位和后2位，中间用*替换，如"138****89"
3. 邮箱：保留用户名前2位和域名，其他用*替换，如"ab***@example.com"
4. 身份证：保留前4位和后2位，中间用*替换
5. 地址：保留省市，详细地址用*替换
6. 银行卡号：保留前4位和后4位，中间用*替换

请按照以下JSON格式返回：
{{
    "masked_text": "脱敏后的文本",
    "masking_operations": [
        {{
            "original": "原始值",
            "masked": "脱敏后的值",
            "category": "PII类别",
            "position": "位置信息"
        }}
    ],
    "masking_summary": "脱敏操作摘要"
}}

只返回JSON格式的结果。"""
        
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
    
    def validate_detection_result(self, result: Dict[str, Any]) -> bool:
        """
        验证检测结果的格式是否正确
        
        Args:
            result: 检测结果字典
            
        Returns:
            是否为有效格式
        """
        required_fields = ['has_pii', 'detected_items', 'risk_level', 'summary']
        return all(field in result for field in required_fields)


# 创建全局实例
pii_detector = PIIDetector()