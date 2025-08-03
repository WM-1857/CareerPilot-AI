import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  Target, 
  Calendar, 
  ThumbsUp, 
  ThumbsDown, 
  MessageSquare,
  TrendingUp,
  User,
  Briefcase,
  Star,
  AlertTriangle
} from 'lucide-react';

const ResultDisplay = ({ results, stageInfo, onFeedback, loading }) => {
  const [feedbackText, setFeedbackText] = useState('');
  const [selectedSatisfaction, setSelectedSatisfaction] = useState('');

  const handleFeedbackSubmit = (satisfaction) => {
    onFeedback(satisfaction, feedbackText);
    setFeedbackText('');
    setSelectedSatisfaction('');
  };

  const renderIntegratedReport = (report) => {
    if (!report) return null;

    return (
      <div className="space-y-6">
        {/* 执行摘要 */}
        {report.executive_summary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                执行摘要
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                {report.executive_summary}
              </p>
            </CardContent>
          </Card>
        )}

        {/* 个人分析 */}
        {report.personal_analysis && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                个人能力分析
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                {report.personal_analysis}
              </p>
            </CardContent>
          </Card>
        )}

        {/* 行业机会 */}
        {report.industry_opportunities && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                行业机会分析
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                {report.industry_opportunities}
              </p>
            </CardContent>
          </Card>
        )}

        {/* 职业匹配度 */}
        {report.career_match && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5" />
                职业匹配度评估
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {report.career_match.match_score && (
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-500" />
                  <span className="font-semibold">匹配度: {report.career_match.match_score}%</span>
                </div>
              )}
              
              {report.career_match.match_reasons && (
                <div>
                  <h4 className="font-medium mb-2">匹配原因:</h4>
                  <ul className="space-y-1">
                    {report.career_match.match_reasons.map((reason, index) => (
                      <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="w-1 h-1 bg-primary rounded-full mt-2 flex-shrink-0"></span>
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {report.career_match.concerns && (
                <div>
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    关注点:
                  </h4>
                  <ul className="space-y-1">
                    {report.career_match.concerns.map((concern, index) => (
                      <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="w-1 h-1 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></span>
                        {concern}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* 发展建议 */}
        {report.development_plan && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                发展建议
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="short_term" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="short_term">短期建议</TabsTrigger>
                  <TabsTrigger value="medium_term">中期建议</TabsTrigger>
                  <TabsTrigger value="long_term">长期建议</TabsTrigger>
                </TabsList>
                
                <TabsContent value="short_term" className="space-y-2">
                  {report.development_plan.short_term?.map((item, index) => (
                    <div key={index} className="p-3 bg-muted rounded-lg">
                      <p className="text-sm">{item}</p>
                    </div>
                  ))}
                </TabsContent>
                
                <TabsContent value="medium_term" className="space-y-2">
                  {report.development_plan.medium_term?.map((item, index) => (
                    <div key={index} className="p-3 bg-muted rounded-lg">
                      <p className="text-sm">{item}</p>
                    </div>
                  ))}
                </TabsContent>
                
                <TabsContent value="long_term" className="space-y-2">
                  {report.development_plan.long_term?.map((item, index) => (
                    <div key={index} className="p-3 bg-muted rounded-lg">
                      <p className="text-sm">{item}</p>
                    </div>
                  ))}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}

        {/* 行动项 */}
        {report.action_items && (
          <Card>
            <CardHeader>
              <CardTitle>具体行动项</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {report.action_items.map((item, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <Badge variant="outline" className="mt-0.5">
                      {index + 1}
                    </Badge>
                    <p className="text-sm">{item}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  const renderCareerGoals = (goals) => {
    if (!goals) return null;

    return (
      <div className="space-y-6">
        {/* 长期目标 */}
        {goals.long_term_goals && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                长期目标 (3-5年)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {goals.long_term_goals.map((goal, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-2">
                  <h4 className="font-semibold">{goal.title}</h4>
                  <p className="text-sm text-muted-foreground">{goal.description}</p>
                  {goal.timeline && (
                    <Badge variant="outline">{goal.timeline}</Badge>
                  )}
                  {goal.success_criteria && (
                    <div>
                      <h5 className="text-sm font-medium">成功标准:</h5>
                      <ul className="text-sm text-muted-foreground">
                        {goal.success_criteria.map((criteria, idx) => (
                          <li key={idx}>• {criteria}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* 中期目标 */}
        {goals.medium_term_goals && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                中期目标 (1-3年)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {goals.medium_term_goals.map((goal, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-2">
                  <h4 className="font-semibold">{goal.title}</h4>
                  <p className="text-sm text-muted-foreground">{goal.description}</p>
                  {goal.timeline && (
                    <Badge variant="outline">{goal.timeline}</Badge>
                  )}
                  {goal.success_criteria && (
                    <div>
                      <h5 className="text-sm font-medium">成功标准:</h5>
                      <ul className="text-sm text-muted-foreground">
                        {goal.success_criteria.map((criteria, idx) => (
                          <li key={idx}>• {criteria}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* 短期目标 */}
        {goals.short_term_goals && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                短期目标 (3-12个月)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {goals.short_term_goals.map((goal, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-2">
                  <h4 className="font-semibold">{goal.title}</h4>
                  <p className="text-sm text-muted-foreground">{goal.description}</p>
                  {goal.timeline && (
                    <Badge variant="outline">{goal.timeline}</Badge>
                  )}
                  {goal.success_criteria && (
                    <div>
                      <h5 className="text-sm font-medium">成功标准:</h5>
                      <ul className="text-sm text-muted-foreground">
                        {goal.success_criteria.map((criteria, idx) => (
                          <li key={idx}>• {criteria}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  const renderFinalPlan = (plan) => {
    if (!plan) return null;

    return (
      <div className="space-y-6">
        {/* 计划概述 */}
        {plan.schedule_overview && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                行动计划概述
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                {plan.schedule_overview}
              </p>
            </CardContent>
          </Card>
        )}

        {/* 学习计划 */}
        {plan.learning_plan && (
          <Card>
            <CardHeader>
              <CardTitle>学习发展计划</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="courses" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="courses">推荐课程</TabsTrigger>
                  <TabsTrigger value="books">推荐书籍</TabsTrigger>
                  <TabsTrigger value="certifications">推荐认证</TabsTrigger>
                </TabsList>
                
                <TabsContent value="courses" className="space-y-2">
                  {plan.learning_plan.courses?.map((course, index) => (
                    <div key={index} className="p-3 bg-muted rounded-lg">
                      <p className="text-sm">{course}</p>
                    </div>
                  ))}
                </TabsContent>
                
                <TabsContent value="books" className="space-y-2">
                  {plan.learning_plan.books?.map((book, index) => (
                    <div key={index} className="p-3 bg-muted rounded-lg">
                      <p className="text-sm">{book}</p>
                    </div>
                  ))}
                </TabsContent>
                
                <TabsContent value="certifications" className="space-y-2">
                  {plan.learning_plan.certifications?.map((cert, index) => (
                    <div key={index} className="p-3 bg-muted rounded-lg">
                      <p className="text-sm">{cert}</p>
                    </div>
                  ))}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}

        {/* 人脉建设 */}
        {plan.networking_plan && (
          <Card>
            <CardHeader>
              <CardTitle>人脉建设建议</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {plan.networking_plan.map((item, index) => (
                  <div key={index} className="p-3 bg-muted rounded-lg">
                    <p className="text-sm">{item}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  if (!results) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* 结果展示 */}
      <Tabs defaultValue="report" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="report">分析报告</TabsTrigger>
          <TabsTrigger value="goals">目标规划</TabsTrigger>
          <TabsTrigger value="plan">行动计划</TabsTrigger>
        </TabsList>
        
        <TabsContent value="report">
          {renderIntegratedReport(results.integrated_report)}
        </TabsContent>
        
        <TabsContent value="goals">
          {renderCareerGoals(results.career_goals)}
        </TabsContent>
        
        <TabsContent value="plan">
          {renderFinalPlan(results.final_plan)}
        </TabsContent>
      </Tabs>

      {/* 用户反馈区域 */}
      {stageInfo?.requires_user_input && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              您的反馈
            </CardTitle>
            <CardDescription>
              请告诉我们您对当前结果的满意度，我们将根据您的反馈进行调整
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="请输入您的具体反馈或建议..."
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              rows={3}
            />
            
            <div className="flex gap-2">
              <Button
                onClick={() => handleFeedbackSubmit('satisfied')}
                disabled={loading}
                className="flex items-center gap-2"
              >
                <ThumbsUp className="h-4 w-4" />
                满意，继续下一步
              </Button>
              
              <Button
                variant="outline"
                onClick={() => handleFeedbackSubmit('dissatisfied')}
                disabled={loading}
                className="flex items-center gap-2"
              >
                <ThumbsDown className="h-4 w-4" />
                需要调整
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ResultDisplay;

