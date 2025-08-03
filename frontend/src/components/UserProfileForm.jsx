import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

const UserProfileForm = ({ onSubmit, loading }) => {
  const [profile, setProfile] = useState({
    user_id: '',
    age: '',
    education_level: '',
    work_experience: '',
    current_position: '',
    industry: '',
    skills: [],
    interests: [],
    career_goals: '',
    location: '',
    salary_expectation: ''
  });

  const [skillInput, setSkillInput] = useState('');
  const [interestInput, setInterestInput] = useState('');
  const [message, setMessage] = useState('');

  const handleInputChange = (field, value) => {
    setProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addSkill = () => {
    if (skillInput.trim() && !profile.skills.includes(skillInput.trim())) {
      setProfile(prev => ({
        ...prev,
        skills: [...prev.skills, skillInput.trim()]
      }));
      setSkillInput('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setProfile(prev => ({
      ...prev,
      skills: prev.skills.filter(skill => skill !== skillToRemove)
    }));
  };

  const addInterest = () => {
    if (interestInput.trim() && !profile.interests.includes(interestInput.trim())) {
      setProfile(prev => ({
        ...prev,
        interests: [...prev.interests, interestInput.trim()]
      }));
      setInterestInput('');
    }
  };

  const removeInterest = (interestToRemove) => {
    setProfile(prev => ({
      ...prev,
      interests: prev.interests.filter(interest => interest !== interestToRemove)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim()) {
      alert('请输入您的职业规划需求');
      return;
    }
    
    // 生成用户ID
    const userId = profile.user_id || `user_${Date.now()}`;
    const finalProfile = {
      ...profile,
      user_id: userId,
      age: profile.age ? parseInt(profile.age) : null,
      work_experience: profile.work_experience ? parseInt(profile.work_experience) : null
    };

    onSubmit(finalProfile, message);
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center">CareerNavigator 职业规划助手</CardTitle>
        <CardDescription className="text-center">
          请填写您的基本信息，我们将为您提供个性化的职业规划建议
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 基本信息 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="age">年龄</Label>
              <Input
                id="age"
                type="number"
                placeholder="请输入年龄"
                value={profile.age}
                onChange={(e) => handleInputChange('age', e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="education">学历水平</Label>
              <Select onValueChange={(value) => handleInputChange('education_level', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="请选择学历" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="高中">高中</SelectItem>
                  <SelectItem value="专科">专科</SelectItem>
                  <SelectItem value="本科">本科</SelectItem>
                  <SelectItem value="硕士">硕士</SelectItem>
                  <SelectItem value="博士">博士</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="experience">工作经验（年）</Label>
              <Input
                id="experience"
                type="number"
                placeholder="工作年限"
                value={profile.work_experience}
                onChange={(e) => handleInputChange('work_experience', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="position">当前职位</Label>
              <Input
                id="position"
                placeholder="如：软件工程师、产品经理等"
                value={profile.current_position}
                onChange={(e) => handleInputChange('current_position', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="industry">所在行业</Label>
              <Input
                id="industry"
                placeholder="如：互联网、金融、教育等"
                value={profile.industry}
                onChange={(e) => handleInputChange('industry', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">所在地区</Label>
              <Input
                id="location"
                placeholder="如：北京、上海、深圳等"
                value={profile.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
              />
            </div>
          </div>

          {/* 技能标签 */}
          <div className="space-y-2">
            <Label>技能标签</Label>
            <div className="flex gap-2">
              <Input
                placeholder="输入技能后按回车添加"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addSkill();
                  }
                }}
              />
              <Button type="button" onClick={addSkill}>添加</Button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {profile.skills.map((skill, index) => (
                <Badge key={index} variant="secondary" className="flex items-center gap-1">
                  {skill}
                  <X 
                    className="h-3 w-3 cursor-pointer" 
                    onClick={() => removeSkill(skill)}
                  />
                </Badge>
              ))}
            </div>
          </div>

          {/* 兴趣爱好 */}
          <div className="space-y-2">
            <Label>兴趣爱好</Label>
            <div className="flex gap-2">
              <Input
                placeholder="输入兴趣后按回车添加"
                value={interestInput}
                onChange={(e) => setInterestInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addInterest();
                  }
                }}
              />
              <Button type="button" onClick={addInterest}>添加</Button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {profile.interests.map((interest, index) => (
                <Badge key={index} variant="outline" className="flex items-center gap-1">
                  {interest}
                  <X 
                    className="h-3 w-3 cursor-pointer" 
                    onClick={() => removeInterest(interest)}
                  />
                </Badge>
              ))}
            </div>
          </div>

          {/* 职业目标 */}
          <div className="space-y-2">
            <Label htmlFor="goals">职业目标</Label>
            <Textarea
              id="goals"
              placeholder="请描述您的职业目标和期望"
              value={profile.career_goals}
              onChange={(e) => handleInputChange('career_goals', e.target.value)}
              rows={3}
            />
          </div>

          {/* 薪资期望 */}
          <div className="space-y-2">
            <Label htmlFor="salary">薪资期望</Label>
            <Input
              id="salary"
              placeholder="如：10-15k、面议等"
              value={profile.salary_expectation}
              onChange={(e) => handleInputChange('salary_expectation', e.target.value)}
            />
          </div>

          {/* 具体需求 */}
          <div className="space-y-2">
            <Label htmlFor="message">您的具体需求 *</Label>
            <Textarea
              id="message"
              placeholder="请详细描述您希望获得什么样的职业规划建议，比如：转行建议、技能提升方向、职业发展路径等"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
              required
            />
          </div>

          <Button 
            type="submit" 
            className="w-full" 
            size="lg"
            disabled={loading}
          >
            {loading ? '正在分析...' : '开始职业规划分析'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default UserProfileForm;

