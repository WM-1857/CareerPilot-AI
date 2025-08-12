"""
阿里云百炼API服务
集成阿里云百炼大模型API，为职业规划系统提供智能分析能力
"""

import os
import json
from typing import Dict, Any, List, Optional
from dashscope import Generation
import dashscope

# Tavily搜索工具集成
import logging
from langchain_community.tools.tavily_search import TavilySearchResults
from searchsrc.config import TAVILY_MAX_RESULTS, TAVILY_API_KEY
from decorators import create_logged_tool

class DashScopeService:
    """阿里云百炼API服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化百炼API服务
        
        Args:
            api_key: 阿里云百炼API密钥，如果不提供则从环境变量获取
        """
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("请设置DASHSCOPE_API_KEY环境变量或提供api_key参数")
        
        dashscope.api_key = self.api_key
        
        # 默认模型配置
        self.default_model = "qwen-plus"
        self.default_temperature = 0.7
        self.default_max_tokens = 2000
    
    def call_llm(self, prompt: str, context: Optional[Dict] = None, 
                 model: Optional[str] = None, temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        调用大语言模型
        
        Args:
            prompt: 输入提示词
            context: 上下文信息
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            包含模型响应的字典
        """
        try:
            # 构建完整的提示词
            full_prompt = self._build_prompt(prompt, context)
            
            # 调用百炼API
            response = Generation.call(
                model=model or self.default_model,
                prompt=full_prompt,
                temperature=temperature or self.default_temperature,
                max_tokens=max_tokens or self.default_max_tokens,
                result_format='message'
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "content": response.output.choices[0].message.content,
                    "usage": response.usage,
                    "request_id": response.request_id
                }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: {response.code} - {response.message}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"调用百炼API时发生异常: {str(e)}"
            }
    
    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        构建完整的提示词
        
        Args:
            prompt: 基础提示词
            context: 上下文信息
            
        Returns:
            完整的提示词
        """
        if not context:
            return prompt
        
        context_str = ""
        if context:
            context_str = "\n\n上下文信息:\n"
            for key, value in context.items():
                if isinstance(value, (dict, list)):
                    context_str += f"{key}: {json.dumps(value, ensure_ascii=False, indent=2)}\n"
                else:
                    context_str += f"{key}: {value}\n"
        
        return f"{context_str}\n\n{prompt}"
    
    def analyze_career_goal_clarity(self, user_request: str, user_profile: Dict) -> Dict[str, Any]:
        """
        分析用户职业目标是否明确
        
        Args:
            user_request: 用户请求
            user_profile: 用户基础信息
            
        Returns:
            分析结果
        """
        prompt = f"""
作为一名专业的职业规划顾问，请分析用户的职业目标是否明确。

用户请求: {user_request}

请从以下几个维度进行分析：
1. 目标职位是否具体明确
2. 行业方向是否清晰
3. 时间规划是否合理
4. 个人能力与目标的匹配度

请以JSON格式返回分析结果：
{{
    "is_goal_clear": true/false,
    "clarity_score": 0-100,
    "reason": "分析原因",
    "missing_info": ["缺失的关键信息"],
    "suggestions": ["改进建议"]
}}
"""
        
        context = {"user_profile": user_profile}
        return self.call_llm(prompt, context)
    
    def create_analysis_strategy(self, user_profile: Dict, feedback_history: List = None) -> Dict[str, Any]:
        """
        制定职业分析策略
        
        Args:
            user_profile: 用户基础信息
            feedback_history: 用户反馈历史
            
        Returns:
            分析策略
        """
        prompt = f"""
作为职业规划专家，请为用户制定一个详细的职业分析策略。

请考虑以下因素：
1. 用户的教育背景和工作经验
2. 用户的技能和兴趣
3. 目标行业的发展趋势
4. 市场需求和竞争情况

请以JSON格式返回策略：
{{
    "strategy_overview": "策略概述",
    "analysis_priorities": ["分析重点"],
    "data_sources": ["数据来源"],
    "timeline": "分析时间线",
    "expected_outcomes": ["预期结果"]
}}
"""
        
        context = {
            "user_profile": user_profile,
            "feedback_history": feedback_history or []
        }
        return self.call_llm(prompt, context)
    
    def analyze_user_profile(self, user_data: Dict) -> Dict[str, Any]:
        """
        分析用户个人画像
        
        Args:
            user_data: 用户数据
            
        Returns:
            个人画像分析结果
        """
        prompt = f"""
作为职业测评专家，请对用户进行全面的个人能力画像分析。

请从以下维度进行分析：
1. 核心技能评估
2. 性格特质分析
3. 职业兴趣匹配
4. 发展潜力评估
5. 优势与劣势识别

请以JSON格式返回分析结果：
{{
    "strengths": ["核心优势"],
    "weaknesses": ["需要改进的方面"],
    "personality_traits": ["性格特质"],
    "skill_assessment": {{
        "technical_skills": ["技术技能"],
        "soft_skills": ["软技能"],
        "skill_gaps": ["技能缺口"]
    }},
    "career_interests": ["职业兴趣"],
    "development_potential": "发展潜力评估",
    "recommendations": ["个人发展建议"]
}}
"""
        
        context = {"user_data": user_data}
        return self.call_llm(prompt, context)
    
    def research_industry_trends(self, target_industry: str) -> Dict[str, Any]:
        """
        研究行业趋势
        
        Args:
            target_industry: 目标行业
            
        Returns:
            行业研究结果
        """
        prompt = f"""
作为行业研究专家，请对"{target_industry}"行业进行深入分析。

请从以下角度进行研究：
1. 行业发展现状
2. 未来发展趋势
3. 主要驱动因素
4. 面临的挑战
5. 薪资水平分析
6. 就业前景评估

请以JSON格式返回研究结果：
{{
    "industry_overview": "行业概述",
    "current_status": "发展现状",
    "future_trends": ["未来趋势"],
    "growth_drivers": ["增长驱动因素"],
    "challenges": ["面临挑战"],
    "salary_analysis": {{
        "entry_level": "入门级薪资",
        "mid_level": "中级薪资",
        "senior_level": "高级薪资"
    }},
    "job_prospects": "就业前景",
    "key_companies": ["重点企业"],
    "recommendations": ["行业建议"]
}}
"""
        
        return self.call_llm(prompt)
    
    def analyze_career_opportunities(self, target_career: str, user_profile: Dict) -> Dict[str, Any]:
        """
        分析职业机会
        
        Args:
            target_career: 目标职业
            user_profile: 用户画像
            
        Returns:
            职业分析结果
        """
        prompt = f"""
作为职业发展顾问，请分析"{target_career}"这个职业方向的机会和要求。

请从以下方面进行分析：
1. 职位职责和要求
2. 技能要求分析
3. 职业发展路径
4. 市场需求情况
5. AI替代风险评估
6. 与用户背景的匹配度

请以JSON格式返回分析结果：
{{
    "job_description": "职位描述",
    "key_responsibilities": ["主要职责"],
    "required_skills": {{
        "must_have": ["必备技能"],
        "nice_to_have": ["加分技能"]
    }},
    "career_path": ["职业发展路径"],
    "market_demand": "市场需求分析",
    "ai_replacement_risk": {{
        "risk_level": "低/中/高",
        "risk_factors": ["风险因素"],
        "mitigation_strategies": ["应对策略"]
    }},
    "user_match_score": 0-100,
    "gap_analysis": ["技能缺口"],
    "recommendations": ["职业建议"]
}}
"""
        
        context = {"user_profile": user_profile}
        return self.call_llm(prompt, context)
    
    def generate_integrated_report(self, analysis_results: Dict) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            analysis_results: 各项分析结果
            
        Returns:
            综合报告
        """
        prompt = f"""
作为资深职业规划顾问，请基于以下分析结果，为用户生成一份综合的职业规划报告。

报告应该包括：
1. 执行摘要
2. 个人能力分析总结
3. 行业机会分析
4. 职业匹配度评估
5. 发展建议和行动计划
6. 风险提示

请以JSON格式返回报告：
{{
    "executive_summary": "执行摘要",
    "personal_analysis": "个人分析总结",
    "industry_opportunities": "行业机会分析",
    "career_match": {{
        "match_score": 0-100,
        "match_reasons": ["匹配原因"],
        "concerns": ["关注点"]
    }},
    "development_plan": {{
        "short_term": ["短期建议"],
        "medium_term": ["中期建议"],
        "long_term": ["长期建议"]
    }},
    "action_items": ["具体行动项"],
    "risk_warnings": ["风险提示"],
    "next_steps": ["下一步行动"]
}}
"""
        
        context = {"analysis_results": analysis_results}
        return self.call_llm(prompt, context)
    
    def decompose_career_goals(self, career_direction: str, user_profile: Dict) -> Dict[str, Any]:
        """
        拆分职业目标
        
        Args:
            career_direction: 职业方向
            user_profile: 用户画像
            
        Returns:
            目标拆分结果
        """
        prompt = f"""
作为职业规划专家，请将用户的职业目标拆分为具体的、可执行的阶段性目标。

职业方向: {career_direction}

请按照SMART原则（具体、可衡量、可达成、相关性、时限性）制定目标：

请以JSON格式返回目标拆分：
{{
    "long_term_goals": [
        {{
            "title": "目标标题",
            "description": "详细描述",
            "timeline": "3-5年",
            "success_criteria": ["成功标准"],
            "required_skills": ["所需技能"],
            "milestones": ["关键里程碑"]
        }}
    ],
    "medium_term_goals": [
        {{
            "title": "目标标题",
            "description": "详细描述",
            "timeline": "1-3年",
            "success_criteria": ["成功标准"],
            "required_skills": ["所需技能"],
            "milestones": ["关键里程碑"]
        }}
    ],
    "short_term_goals": [
        {{
            "title": "目标标题",
            "description": "详细描述",
            "timeline": "3-12个月",
            "success_criteria": ["成功标准"],
            "required_skills": ["所需技能"],
            "milestones": ["关键里程碑"]
        }}
    ]
}}
"""
        
        context = {"user_profile": user_profile}
        return self.call_llm(prompt, context)
    
    def create_action_schedule(self, career_goals: List[Dict], user_constraints: Dict) -> Dict[str, Any]:
        """
        创建行动计划
        
        Args:
            career_goals: 职业目标列表
            user_constraints: 用户约束条件
            
        Returns:
            行动计划
        """
        prompt = f"""
作为时间管理和职业规划专家，请基于用户的职业目标，制定详细的行动计划。

请考虑用户的时间约束和实际情况，制定可执行的计划：

请以JSON格式返回行动计划：
{{
    "schedule_overview": "计划概述",
    "weekly_schedule": [
        {{
            "week": 1,
            "focus_area": "重点领域",
            "tasks": [
                {{
                    "task": "具体任务",
                    "duration": "所需时间",
                    "priority": "优先级",
                    "resources": ["所需资源"]
                }}
            ]
        }}
    ],
    "monthly_milestones": [
        {{
            "month": 1,
            "milestone": "月度里程碑",
            "deliverables": ["交付成果"],
            "success_metrics": ["成功指标"]
        }}
    ],
    "learning_plan": {{
        "courses": ["推荐课程"],
        "books": ["推荐书籍"],
        "certifications": ["推荐认证"]
    }},
    "networking_plan": ["人脉建设建议"],
    "progress_tracking": ["进度跟踪方法"]
}}
"""
        
        context = {
            "career_goals": career_goals,
            "user_constraints": user_constraints
        }
        return self.call_llm(prompt, context)


# 创建全局服务实例
llm_service = DashScopeService()




logger = logging.getLogger(__name__)

# 初始化Tavily搜索工具
LoggedTavilySearch = create_logged_tool(TavilySearchResults)
tavily_tool = LoggedTavilySearch(
    name="tavily_search", 
    max_results=TAVILY_MAX_RESULTS,
    tavily_api_key=TAVILY_API_KEY
)

# 真实的外部API调用函数
def call_mcp_api(api_name: str, params: Dict) -> Dict:
    """
    调用真实的外部API获取数据
    使用Tavily搜索工具获取最新的行业和职位信息
    """
    print(f"--- 外部API调用 ---")
    print(f"API: {api_name}, Params: {params}")
    
    try:
        if api_name == "user_profile_analysis":
            # 搜索用户画像相关的职业测评信息
            search_query = f"职业测评 个人能力分析 {params.get('user_profile', {}).get('current_position', '')}"
            search_results = tavily_tool.invoke({"query": search_query})
            
            # 直接返回Tavily获取到的文本信息
            return {
                "search_results": search_results,
                "data_sources": [result.get("url", "") for result in search_results if isinstance(result, dict)]
            }
            
        elif api_name == "industry_data":
            # 搜索行业趋势和薪资数据
            target_industry = params.get("target_industry", "科技行业")
            search_query = f"{target_industry} 行业趋势 薪资水平 2024"
            search_results = tavily_tool.invoke({"query": search_query})
            
            # 直接返回Tavily获取到的文本信息
            return {
                "search_results": search_results,
                "data_sources": [result.get("url", "") for result in search_results if isinstance(result, dict)]
            }
            
        elif api_name == "job_market":
            # 搜索职位市场信息
            target_career = params.get("target_career", "产品经理")
            search_query = f"{target_career} 职位要求 薪资 招聘 2024"
            search_results = tavily_tool.invoke({"query": search_query})
            
            # 直接返回Tavily获取到的文本信息
            return {
                "search_results": search_results,
                "data_sources": [result.get("url", "") for result in search_results if isinstance(result, dict)]
            }
        
        else:
            logger.warning(f"未知的API调用: {api_name}")
            return {"error": f"未知的API: {api_name}"}
            
    except Exception as e:
        logger.error(f"API调用失败: {api_name}, 错误: {str(e)}")
        return {"error": f"API调用失败: {str(e)}"}

