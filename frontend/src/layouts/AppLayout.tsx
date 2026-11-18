import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Microscope,
  BookOpen,
  Gauge,
  History,
  FileText,
  Activity,
  Sparkles,
  Trophy,
  ChevronRight,
  Fish,
  Search,
} from 'lucide-react';
import { SampleGalleryModal } from '../components/SampleGalleryModal';
import { ChallengeModeModal } from '../components/ChallengeModeModal';
import type { SampleSpecimen } from '../types';
import { api } from '../services/api';

export const AppLayout: React.FC = () => {
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const [isChallengeOpen, setIsChallengeOpen] = useState(false);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const check = () => {
      api
        .checkHealth()
        .then(() => setBackendOnline(true))
        .catch(() => setBackendOnline(false));
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectSample = (sample: SampleSpecimen) => {
    navigate('/workspace', { state: { selectedSample: sample } });
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/catalog?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  const navItems = [
    { to: '/', label: 'Overview & Dashboard', icon: LayoutDashboard },
    { to: '/workspace', label: 'Recognition Workspace', icon: Microscope },
    { to: '/catalog', label: 'Species Catalog', icon: BookOpen, badge: '152 taxa' },
    { to: '/benchmarks', label: 'Model Benchmarks', icon: Gauge, badge: '5 models' },
    { to: '/history', label: 'Prediction History', icon: History },
    { to: '/methodology', label: 'Methodology & About', icon: FileText },
  ];

  return (
    <div className="min-h-screen bg-background text-on-surface flex">
      {/* 1. FIXED LEFT SIDEBAR */}
      <aside className="fixed left-0 top-0 h-full w-72 bg-surface-low border-r border-surface-highest/60 backdrop-blur-xl z-50 flex flex-col justify-between p-4 shadow-[0_8px_32px_-4px_rgba(0,8,20,0.6)]">
        <div className="flex flex-col gap-5">
          {/* Logo & Brand Header */}
          <div className="flex items-center gap-3 px-1 pt-1">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-background shadow-lg shadow-primary/20">
              <Fish className="w-6 h-6 stroke-[2.2]" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-base text-primary tracking-tight">
                  FishVision AI
                </span>
                <span className="text-[10px] font-mono bg-surface-container border border-primary/20 text-secondary px-1.5 py-0.5 rounded-full">
                  v2.4-academic
                </span>
              </div>
              <span className="text-xs text-muted">Deep Oceanic Bio-Vision Lab</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col gap-1 mt-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm transition-all ${
                    isActive
                      ? 'bg-primary text-background font-bold shadow-lg shadow-primary/20'
                      : 'text-muted hover:bg-surface-high hover:text-on-surface'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <item.icon className={`w-4 h-4 ${isActive ? 'text-background' : 'text-muted'}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                          isActive
                            ? 'bg-background/20 text-background font-bold'
                            : 'bg-surface-highest text-secondary'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Quick Interactive Launchers */}
          <div className="pt-2 border-t border-surface-highest/60 flex flex-col gap-2">
            <div className="text-[10px] font-mono uppercase tracking-wider text-muted px-2">
              Interactive Tools
            </div>
            <button
              onClick={() => setIsGalleryOpen(true)}
              className="flex items-center justify-between px-3 py-2 rounded-xl bg-surface-container hover:bg-surface-high border border-surface-highest text-xs text-on-surface hover:text-primary transition-all group"
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-primary group-hover:rotate-12 transition-transform" />
                <span>Sample Gallery (152)</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-muted group-hover:translate-x-0.5 transition-transform" />
            </button>

            <button
              onClick={() => setIsChallengeOpen(true)}
              className="flex items-center justify-between px-3 py-2 rounded-xl bg-surface-container hover:bg-surface-high border border-surface-highest text-xs text-on-surface hover:text-secondary transition-all group"
            >
              <div className="flex items-center gap-2">
                <Trophy className="w-3.5 h-3.5 text-secondary group-hover:scale-110 transition-transform" />
                <span>Fish Quiz Challenge</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-muted group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </div>

        {/* Live System Status Card */}
        <div className="p-3.5 rounded-xl bg-surface-container/70 border border-surface-highest flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono text-primary uppercase tracking-wider">
              System Telemetry
            </span>
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  backendOnline === true
                    ? 'bg-secondary animate-pulse shadow-[0_0_8px_rgba(71,239,214,0.8)]'
                    : backendOnline === false
                    ? 'bg-rose-500'
                    : 'bg-yellow-500 animate-ping'
                }`}
              />
              <span className="text-[10px] font-mono text-secondary">
                {backendOnline === true ? 'Live' : backendOnline === false ? 'Offline' : 'Connecting'}
              </span>
            </div>
          </div>
          <div className="text-xs font-bold text-on-surface">5 / 5 Fine-Tuned Models</div>
          <div className="text-[11px] text-muted font-mono leading-tight">
            DINOv2, ViT-B/16, ConvNeXt, Swin, MobileNetV3
          </div>
        </div>
      </aside>

      {/* 2. MAIN LAYOUT WRAPPER */}
      <div className="pl-72 flex-1 flex flex-col min-w-0">
        {/* Fixed Top Header */}
        <header className="sticky top-0 h-16 bg-surface-low/80 backdrop-blur-xl border-b border-surface-highest/60 z-40 px-6 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 flex-1">
            <div className="hidden xl:flex items-center gap-1.5 text-xs font-mono text-muted">
              <Activity className="w-4 h-4 text-primary" />
              <span>DATASET:</span>
              <span className="text-secondary font-bold">22,741 Benchmark Samples</span>
            </div>

            {/* Global Taxa Search Form */}
            <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
              <input
                type="text"
                placeholder="Search across 152 taxa, common, or scientific names..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 bg-surface-container rounded-lg border border-surface-highest text-xs text-on-surface focus:outline-none focus:border-primary placeholder:text-muted/60"
              />
            </form>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsChallengeOpen(true)}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container hover:bg-surface-high border border-surface-highest text-xs text-secondary font-medium transition-colors"
            >
              <Trophy className="w-3.5 h-3.5" />
              <span>Fish Challenge</span>
            </button>

            <button
              onClick={() => navigate('/workspace')}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-primary text-background text-xs font-bold hover:bg-primary-light transition-all shadow-md glow-cyan"
            >
              <Microscope className="w-4 h-4" />
              <span>Recognition Workspace</span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 relative">
          <div className="absolute top-0 left-1/4 w-[500px] h-[300px] bg-primary/5 rounded-full blur-[140px] pointer-events-none" />
          <div className="absolute top-20 right-10 w-[400px] h-[300px] bg-secondary/5 rounded-full blur-[120px] pointer-events-none" />

          <Outlet />
        </main>
      </div>

      {/* Global Modals */}
      <SampleGalleryModal
        isOpen={isGalleryOpen}
        onClose={() => setIsGalleryOpen(false)}
        onSelectSample={handleSelectSample}
      />

      <ChallengeModeModal
        isOpen={isChallengeOpen}
        onClose={() => setIsChallengeOpen(false)}
      />
    </div>
  );
};
