import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Menu, Search, Bell, User } from 'lucide-react';

interface TopBarProps {
    onMenuClick: () => void;
    className?: string;
    userName?: string;
}

export function TopBar({ onMenuClick, className = '', userName }: TopBarProps) {
    return (
        <div className={`h-16 border-b bg-background flex items-center px-4 justify-between ${className}`}>
            {/* Left: Hamburger & Brand (Mobile) / Breadcrumbs (Desktop) */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" className="lg:hidden" onClick={onMenuClick}>
                    <Menu className="h-6 w-6" />
                </Button>
                <span className="font-semibold text-lg hidden lg:block text-primary">
                    Dashboard
                </span>
                <span className="font-bold text-xl lg:hidden text-primary">
                    KrishiSaarthi
                </span>
            </div>

            {/* Center: Search Bar (Desktop) */}
            <div className="hidden lg:flex flex-1 max-w-xl mx-8">
                <div className="relative w-full">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        type="search"
                        placeholder="Search fields, crops, or help..."
                        className="pl-9 w-full bg-muted/50"
                    />
                </div>
            </div>

            {/* Right: Actions */}
            <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" className="text-muted-foreground relative">
                    <Bell className="h-5 w-5" />
                    <span className="absolute top-1.5 right-1.5 h-2 w-2 bg-red-500 rounded-full" />
                </Button>

                {/* Mobile Profile Icon (Desktop has profile in Sidebar, or we can move it here) */}
                <div className="lg:hidden">
                    <Button variant="ghost" size="icon">
                        <User className="h-5 w-5" />
                    </Button>
                </div>

                <div className="hidden lg:flex items-center gap-2 ml-2">
                    <span className="text-sm font-medium text-muted-foreground">
                        {userName || 'Farmer'}
                    </span>
                    <div className="h-8 w-8 bg-primary/10 rounded-full flex items-center justify-center border border-primary/20">
                        <User className="h-4 w-4 text-primary" />
                    </div>
                </div>
            </div>
        </div>
    );
}
