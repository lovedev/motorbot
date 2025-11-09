/**
 * Learning Center Page
 * Educational resources and guides
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { BookOpen, Play, FileText, HelpCircle } from 'lucide-react';

interface GuideItem {
  id: string;
  title: string;
  titleKo: string;
  description: string;
  descriptionKo: string;
  icon: React.ReactNode;
  category: string;
}

const LearningCenter: React.FC = () => {
  const { i18n, t } = useTranslation();

  const guides: GuideItem[] = [
    {
      id: 'intro',
      title: 'Getting Started',
      titleKo: '시작하기',
      description: 'Learn the basics of motor control and setup',
      descriptionKo: '모터 제어 및 설정의 기본을 배우세요',
      icon: <Play className="w-6 h-6" />,
      category: 'Beginner',
    },
    {
      id: 'calibration',
      title: 'Calibration Guide',
      titleKo: '캘리브레이션 가이드',
      description: 'Step-by-step guide to calibrate your motors',
      descriptionKo: '모터 캘리브레이션 단계별 가이드',
      icon: <FileText className="w-6 h-6" />,
      category: 'Intermediate',
    },
    {
      id: 'telemetry',
      title: 'Telemetry Monitoring',
      titleKo: '원격측정 모니터링',
      description: 'Understand and interpret motor telemetry data',
      descriptionKo: '모터 원격측정 데이터 이해 및 해석',
      icon: <BookOpen className="w-6 h-6" />,
      category: 'Intermediate',
    },
    {
      id: 'troubleshoot',
      title: 'Troubleshooting',
      titleKo: '문제 해결',
      description: 'Common issues and solutions',
      descriptionKo: '일반적인 문제 및 해결책',
      icon: <HelpCircle className="w-6 h-6" />,
      category: 'Advanced',
    },
  ];

  return (
    <div className="p-6 md:p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          {t('learning.title')}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          {t('learning.subtitle')}
        </p>
      </div>

      {/* Learning Guides */}
      <div className="space-y-6">
        {['Beginner', 'Intermediate', 'Advanced'].map((category) => (
          <div key={category}>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {category}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {guides
                .filter((guide) => guide.category === category)
                .map((guide) => (
                  <button
                    key={guide.id}
                    className="p-6 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-blue-300 dark:hover:border-blue-700 hover:shadow-md transition-all text-left"
                  >
                    <div className="flex items-start gap-4">
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-blue-600 dark:text-blue-400">
                        {guide.icon}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {i18n.language === 'ko' ? guide.titleKo : guide.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                          {i18n.language === 'ko'
                            ? guide.descriptionKo
                            : guide.description}
                        </p>
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-3 font-medium">
                          Read Guide →
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Links */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
          {i18n.language === 'ko' ? '빠른 링크' : 'Quick Links'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="#faq"
            className="text-blue-700 dark:text-blue-300 hover:underline font-medium"
          >
            → {i18n.language === 'ko' ? 'FAQ' : 'FAQ'}
          </a>
          <a
            href="#api"
            className="text-blue-700 dark:text-blue-300 hover:underline font-medium"
          >
            → {i18n.language === 'ko' ? 'API 문서' : 'API Documentation'}
          </a>
          <a
            href="#community"
            className="text-blue-700 dark:text-blue-300 hover:underline font-medium"
          >
            → {i18n.language === 'ko' ? '커뮤니티' : 'Community'}
          </a>
        </div>
      </div>
    </div>
  );
};

export default LearningCenter;
