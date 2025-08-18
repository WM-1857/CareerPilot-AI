"""
CareerNavigator 日志工具
提供统一的日志记录和调试输出功能
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import json
from enum import Enum


class CustomJsonEncoder(json.JSONEncoder):
    """自定义JSON编码器，用于处理枚举和日期时间类型"""
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CareerNavigatorLogger:
    """CareerNavigator专用日志类"""
    
    def __init__(self, name: str = "CareerNavigator"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志配置"""
        # 设置日志级别
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        # 控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件输出
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"{self.name.lower()}_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """调试级别日志"""
        log_message = self._format_message(message, extra_data)
        self.logger.debug(log_message)
    
    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """信息级别日志"""
        log_message = self._format_message(message, extra_data)
        self.logger.info(log_message)
    
    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """警告级别日志"""
        log_message = self._format_message(message, extra_data)
        self.logger.warning(log_message)
    
    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """错误级别日志"""
        log_message = self._format_message(message, extra_data)
        self.logger.error(log_message, exc_info=exc_info)
    
    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """严重错误级别日志"""
        log_message = self._format_message(message, extra_data)
        self.logger.critical(log_message)
    
    def _format_message(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> str:
        """格式化日志消息"""
        if extra_data:
            try:
                formatted_data = json.dumps(extra_data, ensure_ascii=False, indent=2, cls=CustomJsonEncoder)
                return f"{message}\n附加数据: {formatted_data}"
            except Exception as e:
                return f"{message}\n附加数据格式化失败: {str(e)}"
        return message


class DebugTracker:
    """调试追踪器 - 用于追踪工作流执行过程"""
    
    def __init__(self, logger: CareerNavigatorLogger):
        self.logger = logger
        self.execution_steps = []
        self.current_session_id = None
    
    def start_session(self, session_id: str, user_profile: Dict[str, Any]):
        """开始新的会话追踪"""
        self.current_session_id = session_id
        self.execution_steps = []
        
        self.logger.info(
            f"🚀 开始新的职业规划会话",
            {
                "session_id": session_id,
                "user_profile": user_profile,
                "start_time": datetime.now().isoformat()
            }
        )
        
        self._add_step("session_start", "会话初始化", user_profile)
    
    def track_node_execution(self, node_name: str, input_data: Dict[str, Any], 
                           output_data: Dict[str, Any], execution_time: float):
        """追踪节点执行"""
        step_data = {
            "node_name": node_name,
            "input_data": input_data,
            "output_data": output_data,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.debug(
            f"🔄 节点执行: {node_name}",
            step_data
        )
        
        self._add_step("node_execution", f"执行节点: {node_name}", step_data)
    
    def track_state_change(self, old_state: Dict[str, Any], new_state: Dict[str, Any]):
        """追踪状态变化"""
        changes = self._detect_state_changes(old_state, new_state)
        
        if changes:
            self.logger.debug(
                "📊 状态变化检测",
                {
                    "session_id": self.current_session_id,
                    "changes": changes,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self._add_step("state_change", "状态更新", changes)
    
    def track_error(self, error_type: str, error_message: str, context: Dict[str, Any]):
        """追踪错误"""
        error_data = {
            "error_type": error_type,
            "error_message": error_message,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.error(
            f"❌ 执行错误: {error_type}",
            error_data
        )
        
        self._add_step("error", f"错误: {error_type}", error_data)
    
    def track_user_feedback(self, feedback_data: Dict[str, Any]):
        """追踪用户反馈"""
        self.logger.info(
            "💬 用户反馈收到",
            {
                "session_id": self.current_session_id,
                "feedback": feedback_data,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        self._add_step("user_feedback", "用户反馈", feedback_data)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        return {
            "session_id": self.current_session_id,
            "total_steps": len(self.execution_steps),
            "execution_steps": self.execution_steps,
            "summary_generated_at": datetime.now().isoformat()
        }
    
    def _add_step(self, step_type: str, description: str, data: Dict[str, Any]):
        """添加执行步骤"""
        step = {
            "step_id": len(self.execution_steps) + 1,
            "step_type": step_type,
            "description": description,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.execution_steps.append(step)
    
    def _detect_state_changes(self, old_state: Dict[str, Any], new_state: Dict[str, Any]) -> Dict[str, Any]:
        """检测状态变化"""
        changes = {}
        
        # 检测关键字段的变化
        key_fields = [
            "current_stage", "iteration_count", "is_analysis_complete", 
            "is_planning_complete", "requires_user_input"
        ]
        
        for field in key_fields:
            old_value = old_state.get(field)
            new_value = new_state.get(field)
            
            if old_value != new_value:
                changes[field] = {
                    "old": old_value,
                    "new": new_value
                }
        
        return changes


# 全局日志实例
main_logger = CareerNavigatorLogger("Main")
workflow_logger = CareerNavigatorLogger("Workflow")
api_logger = CareerNavigatorLogger("API")
llm_logger = CareerNavigatorLogger("LLM")

# 全局调试追踪器
debug_tracker = DebugTracker(workflow_logger)


def log_api_request(method: str, endpoint: str, request_data: Optional[Dict[str, Any]] = None):
    """记录API请求"""
    api_logger.info(
        f"📥 API请求: {method} {endpoint}",
        {
            "method": method,
            "endpoint": endpoint,
            "request_data": request_data,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_api_response(endpoint: str, status_code: int, response_data: Optional[Dict[str, Any]] = None):
    """记录API响应"""
    api_logger.info(
        f"📤 API响应: {endpoint} - {status_code}",
        {
            "endpoint": endpoint,
            "status_code": status_code,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_llm_call(service: str, prompt: str, response: str, cost_info: Optional[Dict[str, Any]] = None):
    """记录LLM调用"""
    llm_logger.info(
        f"🤖 LLM调用: {service}",
        {
            "service": service,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "cost_info": cost_info,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    # 调试模式下记录完整内容
    if os.getenv('LOG_LEVEL', '').upper() == 'DEBUG':
        llm_logger.debug(
            f"🤖 LLM详细内容: {service}",
            {
                "prompt": prompt,
                "response": response
            }
        )
