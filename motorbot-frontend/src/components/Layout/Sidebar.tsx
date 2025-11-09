/**
 * Sidebar Component
 * Navigation sidebar with menu items
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import {
  Settings,
  Zap,
  BarChart3,
  BookOpen,
  Home,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

interface MenuItem {
  id: string;
  label: string;
  labelKo: string;
  icon: React.ReactNode;
  path: string;
  badge?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const { i18n } = useTranslation();
  const location = useLocation();

  const menuItems: MenuItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      labelKo: '대시보드',
      icon: <Home className="w-5 h-5" />,
      path: '/',
    },
    {
      id: 'setup',
      label: 'Setup MotorBus',
      labelKo: '모터버스 설정',
      icon: <Zap className="w-5 h-5" />,
      path: '/setup',
    },
    {
      id: 'calibration',
      label: 'Calibration',
      labelKo: '캘리브레이션',
      icon: <Settings className="w-5 h-5" />,
      path: '/calibration',
    },
    {
      id: 'lerobot',
      label: 'LeRobot Dashboard',
      labelKo: 'LeRobot 대시보드',
      icon: <BarChart3 className="w-5 h-5" />,
      path: '/lerobot',
    },
    {
      id: 'learning',
      label: 'Learning Center',
      labelKo: '학습 센터',
      icon: <BookOpen className="w-5 h-5" />,
      path: '/learning',
    },
  ];

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed md:static left-0 top-16 md:top-0 bottom-0 md:bottom-auto w-64 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 z-20 transition-transform duration-300 ease-in-out overflow-y-auto',
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        <div className="flex flex-col h-full p-4 md:p-6">
          {/* Close Button (Mobile) */}
          <button
            onClick={onClose}
            className="md:hidden p-2 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-lg self-end -mr-2 mb-4"
          >
            <X className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>

          {/* Sidebar Header */}
          <div className="mb-6">
            <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              {i18n.language === 'ko' ? '메뉴' : 'Menu'}
            </h2>
          </div>

          {/* Menu Items */}
          <nav className="flex flex-col gap-1 flex-1">
            {menuItems.map((item) => {
              const active = isActive(item.path);
              return (
                <Link
                  key={item.id}
                  to={item.path}
                  onClick={onClose}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200',
                    active
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 font-medium'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  )}
                >
                  <span className={cn('transition-colors', active && 'text-blue-600 dark:text-blue-400')}>
                    {item.icon}
                  </span>
                  <span className="flex-1">
                    {i18n.language === 'ko' ? item.labelKo : item.label}
                  </span>
                  {item.badge && (
                    <span className="px-2 py-1 text-xs font-semibold bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Divider */}
          <div className="my-4 border-t border-gray-200 dark:border-gray-800" />

          {/* Quick Stats */}
          <div className="space-y-3 mt-auto">
            <div className="px-4 py-3 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-100 dark:border-blue-800/50">
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {i18n.language === 'ko' ? '모터 상태' : 'Motor Status'}
              </p>
              <p className="text-lg font-bold text-blue-700 dark:text-blue-400 mt-1">
                12 / 12
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {i18n.language === 'ko' ? '활성화됨' : 'Active'}
              </p>
            </div>

            <div className="px-4 py-3 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-100 dark:border-green-800/50">
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {i18n.language === 'ko' ? '캘리브레이션' : 'Calibrated'}
              </p>
              <p className="text-lg font-bold text-green-700 dark:text-green-400 mt-1">
                8 / 12
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {i18n.language === 'ko' ? '완료됨' : 'Complete'}
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
