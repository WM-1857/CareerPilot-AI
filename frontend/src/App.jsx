import React, { useState, useEffect } from 'react';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';
import UserProfileForm from './components/UserProfileForm';
import PlanningProgress from './components/PlanningProgress';
import ResultDisplay from './components/ResultDisplay';
import './App.css';

const API_BASE_URL = '/api/career';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [stageInfo, setStageInfo] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  // 轮询获取状态更新
  useEffect(() => {
    if (!sessionId) return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/status/${sessionId}`);
        if (response.ok) {
          const data = await response.json();
          setStageInfo(data.stage_info);
          setResults(data.results);
        }
      } catch (error) {
        console.error('获取状态失败:', error);
      }
    };

    // 立即执行一次
    pollStatus();

    // 每5秒轮询一次
    const interval = setInterval(pollStatus, 5050);
    return () => clearInterval(interval);
  }, [sessionId]);

  const handleStartPlanning = async (userProfile, message) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_profile: userProfile,
          message: message
        })
      });

      const data = await response.json();

      if (data.success) {
        setSessionId(data.session_id);
        setStageInfo(data.stage_info);
        toast.success("规划已开始", {
          description: "我们正在为您分析职业规划方案，请稍候...",
        });
      } else {
        toast.error("启动失败", {
          description: data.error || "请稍后重试",
        });
      }
    } catch (error) {
      console.error('启动规划失败:', error);
      toast.error("网络错误", {
        description: "请检查网络连接后重试",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (satisfactionLevel, feedbackText) => {
    if (!sessionId) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/feedback/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          satisfaction_level: satisfactionLevel,
          feedback_text: feedbackText
        })
      });

      const data = await response.json();

      if (data.success) {
        setStageInfo(data.stage_info);
        toast.success("反馈已提交", {
          description: data.message,
        });
      } else {
        toast.error("提交失败", {
          description: data.error || "请稍后重试",
        });
      }
    } catch (error) {
      console.error('提交反馈失败:', error);
      toast.error("网络错误", {
        description: "请检查网络连接后重试",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setStageInfo(null);
    setResults(null);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            CareerNavigator
          </h1>
          <p className="text-xl text-gray-600">
            基于AI的智能职业规划助手
          </p>
        </div>

        {/* 主要内容 */}
        {!sessionId ? (
          // 用户信息表单
          <UserProfileForm 
            onSubmit={handleStartPlanning}
            loading={loading}
          />
        ) : (
          // 规划进度和结果展示
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 左侧：进度显示 */}
            <div className="lg:col-span-1">
              <PlanningProgress 
                stageInfo={stageInfo}
                sessionId={sessionId}
              />
              
              {/* 重新开始按钮 */}
              <div className="mt-4">
                <button
                  onClick={handleReset}
                  className="w-full px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  重新开始规划
                </button>
              </div>
            </div>

            {/* 右侧：结果展示 */}
            <div className="lg:col-span-2">
              <ResultDisplay
                results={results}
                stageInfo={stageInfo}
                onFeedback={handleFeedback}
                loading={loading}
              />
            </div>
          </div>
        )}

        {/* 页脚 */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>
            Powered by LangGraph & 阿里云百炼 | 
            <span className="ml-2">
              让AI为您的职业发展保驾护航
            </span>
          </p>
        </div>
      </div>

      <Toaster />
    </div>
  );
}

export default App;
