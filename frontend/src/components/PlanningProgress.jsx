import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Clock, AlertCircle, User, BarChart3, Target, Calendar } from 'lucide-react';

const PlanningProgress = ({ stageInfo, sessionId }) => {
  const getStageIcon = (stageName) => {
    const icons = {
      '初始化': Clock,
      '策略制定': User,
      '并行分析': BarChart3,
      '结果整合': BarChart3,
      '用户反馈': User,
      '目标拆分': Target,
      '日程规划': Calendar,
      '最终确认': CheckCircle,
      '完成': CheckCircle
    };
    return icons[stageName] || Clock;
  };

  const getStageProgress = (stageName) => {
    const progressMap = {
      '初始化': 10,
      '策略制定': 20,
      '并行分析': 40,
      '结果整合': 60,
      '用户反馈': 70,
      '目标拆分': 80,
      '日程规划': 90,
      '最终确认': 95,
      '完成': 100
    };
    return progressMap[stageName] || 0;
  };

  const getStageColor = (stageName) => {
    const colorMap = {
      '初始化': 'bg-blue-500',
      '策略制定': 'bg-purple-500',
      '并行分析': 'bg-orange-500',
      '结果整合': 'bg-green-500',
      '用户反馈': 'bg-yellow-500',
      '目标拆分': 'bg-indigo-500',
      '日程规划': 'bg-pink-500',
      '最终确认': 'bg-emerald-500',
      '完成': 'bg-green-600'
    };
    return colorMap[stageName] || 'bg-gray-500';
  };

  if (!stageInfo) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <Clock className="h-6 w-6 animate-spin mr-2" />
            <span>正在初始化...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const Icon = getStageIcon(stageInfo.stage_info?.name);
  const progress = getStageProgress(stageInfo.stage_info?.name);
  const stageColor = getStageColor(stageInfo.stage_info?.name);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon className="h-5 w-5" />
          职业规划进度
          <Badge variant="outline" className="ml-auto">
            {stageInfo.iteration_count}/{stageInfo.max_iterations} 轮
          </Badge>
        </CardTitle>
        <CardDescription>
          会话ID: {sessionId}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 进度条 */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>整体进度</span>
            <span>{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* 当前阶段 */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${stageColor}`}></div>
            <div>
              <h3 className="font-semibold">{stageInfo.stage_info?.name}</h3>
              <p className="text-sm text-muted-foreground">
                {stageInfo.stage_info?.description}
              </p>
            </div>
          </div>

          {/* 下一步行动 */}
          {stageInfo.stage_info?.next_action && (
            <div className="bg-muted p-3 rounded-lg">
              <p className="text-sm">
                <strong>下一步：</strong> {stageInfo.stage_info.next_action}
              </p>
            </div>
          )}

          {/* 等待用户输入提示 */}
          {stageInfo.requires_user_input && (
            <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
              <div className="flex items-center gap-2 text-yellow-800">
                <AlertCircle className="h-4 w-4" />
                <span className="font-medium">需要您的反馈</span>
              </div>
              {stageInfo.pending_questions && stageInfo.pending_questions.length > 0 && (
                <div className="mt-2">
                  {stageInfo.pending_questions.map((question, index) => (
                    <p key={index} className="text-sm text-yellow-700">
                      {question}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* 阶段列表 */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">规划流程</h4>
          <div className="space-y-1">
            {[
              '初始化',
              '策略制定', 
              '并行分析',
              '结果整合',
              '用户反馈',
              '目标拆分',
              '日程规划',
              '最终确认',
              '完成'
            ].map((stage, index) => {
              const isCompleted = getStageProgress(stage) < progress;
              const isCurrent = stage === stageInfo.stage_info?.name;
              
              return (
                <div 
                  key={index}
                  className={`flex items-center gap-2 text-sm p-2 rounded ${
                    isCurrent ? 'bg-primary/10 text-primary' : 
                    isCompleted ? 'text-green-600' : 'text-muted-foreground'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : isCurrent ? (
                    <Clock className="h-4 w-4" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border-2 border-muted-foreground/30"></div>
                  )}
                  <span>{stage}</span>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PlanningProgress;

