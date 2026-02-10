import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useTranslation } from '@/hooks/useTranslation';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/components/layout/ThemeProvider';
import { useField } from '@/context/FieldContext';
import { Sprout, BarChart3, User, Globe, LandPlot, ChartLine, BugOff, CalendarDays, LogOut, Sun, Moon, Plus, IndianRupee, PieChart, Calendar, Package, Users, Tractor, Droplets, Target, RotateCw, Store, TrendingUp, Building2, Shield, Home, AlertCircle } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  className?: string;
}

export function Sidebar({ activeTab, onTabChange, className = '' }: SidebarProps) {
  const { language, setLanguage, t } = useTranslation();
  const { user, logout } = useAuth();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const { fields, selectedField, setSelectedField } = useField();

  const tabs = [
    { id: 'home', icon: Home, label: t('home') },
    { id: 'field-report', icon: BarChart3, label: t('field_report') },
    { id: 'my-field', icon: LandPlot, label: t('my_field') },
    { id: 'data-analytics', icon: ChartLine, label: t('data_analytics') },
    { id: 'field-log', icon: CalendarDays, label: t('field_log') },
    { id: 'pest', icon: BugOff, label: t('pest') },
    { id: 'cost-calculator', icon: IndianRupee, label: t('cost_calculator') },
    { id: 'pnl-dashboard', icon: PieChart, label: t('pnl_dashboard') },
    { id: 'season-calendar', icon: CalendarDays, label: t('season_calendar') },
    { id: 'inventory', icon: Package, label: t('inventory') },
    { id: 'labor', icon: Users, label: t('labor') },
    { id: 'equipment', icon: Tractor, label: t('equipment') },
    { id: 'irrigation', icon: Droplets, label: t('irrigation') },
    { id: 'yield-prediction', icon: Target, label: t('yield_prediction') },
    { id: 'rotation', icon: RotateCw, label: t('crop_rotation') },
    { id: 'market', icon: Store, label: t('market_prices') },
    { id: 'forecast', icon: TrendingUp, label: t('price_forecast') },
    { id: 'schemes', icon: Building2, label: t('govt_schemes') },
    { id: 'insurance', icon: Shield, label: t('insurance') },
    { id: 'alerts', icon: AlertCircle, label: t('alerts') },
  ];

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <div className={`w-64 gradient-bg text-white flex-shrink-0 ${className}`}>
      <div className="p-6 h-full flex flex-col">
        {/* Logo and Brand */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
              <Sprout className="text-primary text-xl" />
            </div>
            <span className="text-xl font-bold">Krishi Sakhi</span>
          </div>
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            className="text-white hover:bg-white/20 p-2"
            title={resolvedTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {resolvedTheme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </div>

        {/* Navigation Menu */}
        <nav className="space-y-2 flex-1">
          {tabs.map((tab) => (
            <Button
              key={tab.id}
              variant="ghost"
              className={`w-full justify-start py-3 px-4 text-white hover:bg-white/20 font-medium transition-colors ${activeTab === tab.id ? 'bg-white/20' : ''
                }`}
              onClick={() => onTabChange(tab.id)}
              data-testid={`tab-${tab.id}`}
            >
              <tab.icon className="mr-3 h-4 w-4" />
              {tab.label}
            </Button>
          ))}
        </nav>

        {/* Field Selector */}
        <div className="mt-6 mb-2">
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium">
              <LandPlot className="inline mr-2 h-4 w-4" />
              Current Field
            </label>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 hover:bg-white/20"
              onClick={() => {
                setSelectedField(null);
                onTabChange('my-field');
              }}
              title="Add New Field"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>

          <Select
            value={selectedField ? String(selectedField.id) : "new"}
            onValueChange={(val) => {
              if (val === "new") {
                setSelectedField(null);
                onTabChange('my-field');
              } else {
                const field = fields.find(f => f.id === Number(val));
                setSelectedField(field || null);
              }
            }}
          >
            <SelectTrigger className="w-full bg-white/20 border-white/30 text-white truncate">
              <SelectValue placeholder="Select Field" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="new">-- New Field --</SelectItem>
              {fields.map(field => (
                <SelectItem key={field.id} value={String(field.id)}>
                  {field.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Language Selector */}
        <div className="mt-8">
          <label className="text-sm font-medium mb-2 block">
            <Globe className="inline mr-2 h-4 w-4" />
            {t('language')}
          </label>
          <Select value={language} onValueChange={(value) => setLanguage(value as any)}>
            <SelectTrigger className="w-full bg-white/20 border-white/30 text-white" data-testid="language-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="en">English</SelectItem>
              <SelectItem value="hi">हिंदी</SelectItem>
              <SelectItem value="pa">ਪੰਜਾਬੀ</SelectItem>
              <SelectItem value="ml">മലയാളം</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* User Profile */}
        <div className="mt-8 p-4 bg-white/20 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center">
                <User className="text-white text-sm" />
              </div>
              <div>
                <p className="font-medium text-sm">{user?.username || t('farmer')}</p>
                <p className="text-xs opacity-75">{t('online')}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-white hover:bg-white/20 p-2"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
