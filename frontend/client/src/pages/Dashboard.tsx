import { useState, useMemo, useEffect, useCallback } from 'react';
import { FieldReport } from '@/components/field/FieldReport';
import { MyField } from '@/components/field/MyField';
import { DataAnalytics } from '@/components/analytics/DataAnalytics';
import ChatBot from '@/components/chat/ChatBot';
import { Pest } from '@/components/field/Pest';
import { FieldLog } from '@/components/field/FieldLog';
import { FieldAlerts } from '@/components/field/FieldAlerts';
import { CostCalculator } from "@/components/finance/CostCalculator";
import { PnLDashboard } from "@/components/finance/PnLDashboard";
import { apiFetch } from "@/lib/api";
import { logger } from "@/lib/logger";
import { SeasonCalendar } from "@/components/planning/SeasonCalendar";
import { InventoryTracker } from "@/components/planning/InventoryTracker";
import { LaborManager } from "@/components/planning/LaborManager";
import { EquipmentScheduler } from "@/components/planning/EquipmentScheduler";
import { IrrigationScheduler } from "@/components/field/IrrigationScheduler";
import { YieldPrediction } from "@/components/field/YieldPrediction";
import { RotationPlanner } from "@/components/planning/RotationPlanner";
import { MarketPrices } from "@/components/finance/MarketPrices";
import { PriceForecast } from "@/components/finance/PriceForecast";
import { SchemeMatcher } from "@/components/finance/SchemeMatcher";
import { InsuranceClaims } from "@/components/finance/InsuranceClaims";
import { HomeDashboard } from "@/components/dashboard/HomeDashboard";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/utils";


// Navigation items configuration with grouping
const navItems = [
  // Core
  { id: 'home', label: 'Dashboard', icon: 'dashboard' },
  { id: 'my-field', label: 'My Field', icon: 'grass' },
  { id: 'field-report', label: 'Field Report', icon: 'monitoring' },
  { id: 'data-analytics', label: 'Analytics', icon: 'query_stats' },
  // Field Operations
  { id: 'field-log', label: 'Field Log', icon: 'event_note' },
  { id: 'pest', label: 'Pest Detection', icon: 'bug_report' },
  { id: 'irrigation', label: 'Irrigation', icon: 'water_drop' },
  { id: 'yield-prediction', label: 'Yield Prediction', icon: 'trending_up' },
  { id: 'alerts', label: 'Alerts', icon: 'notifications' },
  // Planning
  { id: 'season-calendar', label: 'Season Calendar', icon: 'calendar_month' },
  { id: 'rotation', label: 'Crop Rotation', icon: 'autorenew' },
  { id: 'inventory', label: 'Inventory', icon: 'inventory_2' },
  { id: 'labor', label: 'Labor', icon: 'groups' },
  { id: 'equipment', label: 'Equipment', icon: 'agriculture' },
  // Finance & Market
  { id: 'cost-calculator', label: 'Costs & Revenue', icon: 'calculate' },
  { id: 'pnl-dashboard', label: 'Profit & Loss', icon: 'pie_chart' },
  { id: 'market', label: 'Market Prices', icon: 'storefront' },
  { id: 'forecast', label: 'Price Forecast', icon: 'show_chart' },
  { id: 'schemes', label: 'Govt Schemes', icon: 'account_balance' },
  { id: 'insurance', label: 'Insurance', icon: 'shield' },
];

// Tab title mapping
const tabTitles: Record<string, string> = {
  'home': 'Dashboard Overview',
  'my-field': 'Field Management',
  'field-report': 'Field Report',
  'data-analytics': 'Data Analytics',
  'pest': 'Pest Detection',
  'field-log': 'Field Log',
  'cost-calculator': 'Cost Calculator',
  'pnl-dashboard': 'Profit & Loss',
  'season-calendar': 'Season Calendar',
  'inventory': 'Inventory Tracker',
  'labor': 'Labor Management',
  'equipment': 'Equipment Scheduler',
  'irrigation': 'Irrigation Scheduler',
  'yield-prediction': 'Yield Prediction',
  'rotation': 'Crop Rotation',
  'market': 'Market Prices',
  'forecast': 'Price Forecast',
  'schemes': 'Government Schemes',
  'insurance': 'Insurance Claims',
  'alerts': 'Field Alerts',
  'settings': 'Settings',
};

const validTabIds = new Set(navItems.map(item => item.id));

function getTabFromHash(): string {
  const hash = window.location.hash.replace('#', '');
  return validTabIds.has(hash) ? hash : 'home';
}

export default function Dashboard() {
  const [activeTab, setActiveTabState] = useState(getTabFromHash);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { user, token } = useAuth();
  const [unreadAlertCount, setUnreadAlertCount] = useState(0);

  const setActiveTab = useCallback((tab: string) => {
    setActiveTabState(tab);
    window.history.pushState(null, '', `#${tab}`);
  }, []);

  // Sync with browser back/forward
  useEffect(() => {
    const onHashChange = () => setActiveTabState(getTabFromHash());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  // Fetch unread alert count
  useEffect(() => {
    if (!token) return;
    const fetchUnread = async () => {
      try {
        const alerts = await apiFetch<Array<{ is_read: boolean }>>('/field/alerts');
        setUnreadAlertCount(alerts.filter(a => !a.is_read).length);
      } catch {
        // Silently ignore - non-critical
      }
    };
    fetchUnread();
    const interval = setInterval(fetchUnread, 60_000); // Refresh every minute
    return () => clearInterval(interval);
  }, [token]);

  // Filter nav items based on search query
  const filteredNavItems = useMemo(() => {
    if (!searchQuery.trim()) return navItems;
    const q = searchQuery.toLowerCase();
    return navItems.filter(item =>
      item.label.toLowerCase().includes(q) ||
      item.id.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'home': return <HomeDashboard onNavigate={setActiveTab} />;
      case 'field-report': return <FieldReport />;
      case 'my-field': return <MyField />;
      case 'data-analytics': return <DataAnalytics />;
      case 'pest': return <Pest />
      case 'field-log': return <FieldLog />
      case 'cost-calculator': return <CostCalculator />
      case 'pnl-dashboard': return <PnLDashboard onNavigate={setActiveTab} />
      case 'season-calendar': return <SeasonCalendar />
      case 'inventory': return <InventoryTracker />
      case 'labor': return <LaborManager />
      case 'equipment': return <EquipmentScheduler />
      case 'irrigation': return <IrrigationScheduler />
      case 'yield-prediction': return <YieldPrediction />
      case 'rotation': return <RotationPlanner />
      case 'market': return <MarketPrices />
      case 'forecast': return <PriceForecast />
      case 'schemes': return <SchemeMatcher />
      case 'insurance': return <InsuranceClaims />
      case 'alerts': return <FieldAlerts />
      default: return <HomeDashboard onNavigate={setActiveTab} />;
    }
  };

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-foreground font-sans transition-colors duration-200">
      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar - Stitch Design */}
      <aside className={cn(
        "fixed lg:static inset-y-0 left-0 z-50 w-64 flex-shrink-0 flex flex-col",
        "bg-card border-r border-border",
        "transform transition-transform duration-200 ease-in-out",
        isMobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        {/* Logo Section */}
        <div className="p-6 flex items-center gap-3">
          <div className="size-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-primary-foreground shadow-lg shadow-primary/30">
            <span className="material-symbols-outlined">agriculture</span>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">AgriSmart</h1>
            <p className="text-xs text-muted-foreground">Farm Management</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 space-y-1 mt-4 overflow-y-auto">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setActiveTab(item.id);
                setIsMobileMenuOpen(false);
              }}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all duration-150",
                activeTab === item.id
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <span className={cn(
                "material-symbols-outlined transition-colors",
                activeTab === item.id && "fill-1"
              )}>
                {item.icon}
              </span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* User Profile Section */}
        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted cursor-pointer transition-colors">
            <div className="size-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold">
              {user?.username?.charAt(0) || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.username || 'User'}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email || 'user@example.com'}</p>
            </div>
            <span className="material-symbols-outlined text-muted-foreground text-lg"></span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Top Header - Stitch Design */}
        <header className="h-16 flex items-center justify-between px-4 md:px-8 bg-card/80 backdrop-blur-md border-b border-border sticky top-0 z-10">
          {/* Mobile Menu Button */}
          <button
            className="lg:hidden p-2 -ml-2 text-muted-foreground hover:text-foreground"
            onClick={() => setIsMobileMenuOpen(true)}
          >
            <span className="material-symbols-outlined">menu</span>
          </button>

          {/* Page Title */}
          <div className="flex items-center">
            <h2 className="text-lg font-semibold">{tabTitles[activeTab] || 'Dashboard'}</h2>
          </div>

          {/* Header Actions */}
          <div className="flex items-center gap-4">
            {/* Search - Desktop Only */}
            <div className="relative hidden md:block">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-muted-foreground text-xl">search</span>
              <input
                className="w-64 pl-10 pr-4 py-2 bg-muted border-none rounded-full text-sm focus:ring-2 focus:ring-primary/50 placeholder-muted-foreground"
                placeholder="Search data, crops, reports..."
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {/* Search results dropdown */}
              {searchQuery.trim() && filteredNavItems.length > 0 && (
                <div className="absolute top-full mt-1 left-0 w-full bg-card border border-border rounded-lg shadow-lg z-50 overflow-hidden">
                  {filteredNavItems.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        setActiveTab(item.id);
                        setSearchQuery('');
                      }}
                      className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-muted transition-colors text-left"
                    >
                      <span className="material-symbols-outlined text-base text-muted-foreground">{item.icon}</span>
                      {item.label}
                    </button>
                  ))}
                </div>
              )}
              {searchQuery.trim() && filteredNavItems.length === 0 && (
                <div className="absolute top-full mt-1 left-0 w-full bg-card border border-border rounded-lg shadow-lg z-50 px-4 py-3 text-sm text-muted-foreground">
                  No results found
                </div>
              )}
            </div>

            {/* Notifications */}
            <button
              className="relative p-2 text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setActiveTab('alerts')}
              title="View alerts"
            >
              <span className="material-symbols-outlined">notifications</span>
              {unreadAlertCount > 0 && (
                <span className="absolute top-1 right-1 size-4 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full flex items-center justify-center">
                  {unreadAlertCount > 9 ? '9+' : unreadAlertCount}
                </span>
              )}
            </button>

            {/* Mobile Search Button */}
            <button className="md:hidden p-2 text-muted-foreground hover:text-foreground">
              <span className="material-symbols-outlined">search</span>
            </button>
          </div>
        </header>

        {/* Dashboard Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          {renderTabContent()}
        </div>
      </main>

      {/* ChatBot Floating */}
      <ChatBot />
    </div>
  );
}
