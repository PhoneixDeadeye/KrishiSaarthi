import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Building2, FileText, ExternalLink, Calendar, IndianRupee, Filter, Search, CheckCircle2, Clock, AlertCircle, Wallet, GraduationCap, Shield, Gift, RefreshCw, Newspaper } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { logger } from "@/lib/logger";

interface Scheme {
    id: number;
    name: string;
    scheme_type: string;
    description: string;
    benefits: string;
    eligible_crops: string[];
    eligible_states: string[];
    min_land_acres: number;
    max_subsidy_amount: number | null;
    subsidy_percentage?: number;
    documents_required: string[];
    link: string;
    is_active: boolean;
    application_deadline?: string;
    match_score: number;
}

interface SchemesData {
    total_schemes: number;
    user_crops: string[];
    schemes: Scheme[];
    grouped: {
        subsidy: Scheme[];
        loan: Scheme[];
        insurance: Scheme[];
        grant: Scheme[];
        training: Scheme[];
    };
    tips: { icon: string; text: string }[];
    live_schemes_news?: {
        title: string;
        description: string;
        date: string;
        source: string;
    }[];
}

const STATES = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Gujarat', 'Madhya Pradesh', 'Kerala'];
const SCHEME_TYPES = [
    { value: 'all', label: 'All Types', icon: Filter },
    { value: 'subsidy', label: 'Subsidies', icon: Gift },
    { value: 'loan', label: 'Loans', icon: Wallet },
    { value: 'insurance', label: 'Insurance', icon: Shield },
    { value: 'grant', label: 'Grants', icon: IndianRupee },
    { value: 'training', label: 'Training', icon: GraduationCap },
];

export function SchemeMatcher() {
    const [data, setData] = useState<SchemesData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [state, setState] = useState('Punjab');
    const [schemeType, setSchemeType] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [expandedScheme, setExpandedScheme] = useState<number | null>(null);

    const fetchSchemes = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams();
            if (state) params.append('state', state);
            if (schemeType !== 'all') params.append('type', schemeType);

            const response = await apiFetch(`/finance/schemes?${params.toString()}`);
            setData(response as SchemesData);
        } catch (err) {
            setError('Failed to load government schemes');
            logger.error('Failed to load government schemes', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSchemes();
    }, [state, schemeType]);

    const getSchemeTypeIcon = (type: string) => {
        const typeConfig = SCHEME_TYPES.find(t => t.value === type);
        if (typeConfig) {
            const Icon = typeConfig.icon;
            return <Icon className="h-4 w-4" />;
        }
        return <FileText className="h-4 w-4" />;
    };

    const getSchemeTypeBadge = (type: string) => {
        const colors: Record<string, string> = {
            subsidy: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
            loan: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
            insurance: 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400',
            grant: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
            training: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
        };
        return colors[type] || 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
    };

    const getMatchScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-600 dark:text-green-400';
        if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
        return 'text-muted-foreground';
    };

    const formatAmount = (amount: number | null) => {
        if (!amount) return 'Varies';
        return `₹${amount.toLocaleString('en-IN')}`;
    };

    const filteredSchemes = data?.schemes.filter(scheme => {
        if (!searchQuery) return true;
        return scheme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            scheme.description.toLowerCase().includes(searchQuery.toLowerCase());
    }) || [];

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Building2 className="h-6 w-6 text-primary" />
                        Government Schemes
                    </h1>
                    <p className="text-muted-foreground">
                        Find eligible subsidies, loans, and support programs for your farm
                    </p>
                </div>

                <Button variant="outline" onClick={fetchSchemes} disabled={loading}>
                    <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                </Button>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                            <label className="text-sm font-medium mb-1 block">State</label>
                            <Select value={state} onValueChange={setState}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {STATES.map(s => (
                                        <SelectItem key={s} value={s}>{s}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div>
                            <label className="text-sm font-medium mb-1 block">Type</label>
                            <Select value={schemeType} onValueChange={setSchemeType}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {SCHEME_TYPES.map(t => (
                                        <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="md:col-span-2">
                            <label className="text-sm font-medium mb-1 block">Search</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search schemes..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-9"
                                />
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Stats */}
            {data && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20">
                        <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-green-700 dark:text-green-400">{data.grouped.subsidy.length}</div>
                            <div className="text-sm text-green-600 dark:text-green-500">Subsidies</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20">
                        <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-blue-700 dark:text-blue-400">{data.grouped.loan.length}</div>
                            <div className="text-sm text-blue-600 dark:text-blue-500">Loans</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-teal-50 to-teal-100 dark:from-teal-900/20 dark:to-teal-800/20">
                        <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-teal-700 dark:text-teal-400">{data.grouped.insurance.length}</div>
                            <div className="text-sm text-teal-600 dark:text-teal-500">Insurance</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20">
                        <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">{data.grouped.grant.length}</div>
                            <div className="text-sm text-yellow-600 dark:text-yellow-500">Grants</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20">
                        <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-orange-700 dark:text-orange-400">{data.total_schemes}</div>
                            <div className="text-sm text-orange-600 dark:text-orange-500">Total</div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {error && (
                <Card className="border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
                    <CardContent className="p-4 flex items-center gap-2 text-red-700 dark:text-red-400">
                        <AlertCircle className="h-5 w-5" />
                        {error}
                    </CardContent>
                </Card>
            )}

            {/* Live News & Updates */}
            {data?.live_schemes_news && data.live_schemes_news.length > 0 && (
                <Card className="border-blue-200 dark:border-blue-900 bg-blue-50/50 dark:bg-blue-900/10">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-lg flex items-center gap-2 text-blue-800 dark:text-blue-300">
                            <Newspaper className="h-5 w-5" />
                            Live Government Scheme Updates
                            <Badge variant="outline" className="ml-auto bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100 border-blue-300">Live</Badge>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {data.live_schemes_news.map((news, i) => (
                            <div key={i} className="flex flex-col border-b last:border-0 pb-3 last:pb-0 border-blue-100 dark:border-blue-800">
                                <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">{news.title}</h4>
                                <p className="text-sm text-blue-700 dark:text-blue-300 mb-2">{news.description}</p>
                                <div className="flex items-center justify-between text-xs text-blue-600/80 dark:text-blue-400/80">
                                    <span>{new Date(news.date).toLocaleDateString()}</span>
                                    {news.source && (
                                        <a href={news.source} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 hover:underline">
                                            Read More <ExternalLink className="h-3 w-3" />
                                        </a>
                                    )}
                                </div>
                            </div>
                        ))}
                    </CardContent>
                </Card>
            )}

            {/* Schemes List */}
            <div className="space-y-4">
                {filteredSchemes.map(scheme => (
                    <Card key={scheme.id} className="overflow-hidden hover:shadow-md transition-shadow">
                        <CardContent className="p-0">
                            {/* Scheme Header */}
                            <div
                                className="p-4 cursor-pointer"
                                onClick={() => setExpandedScheme(expandedScheme === scheme.id ? null : scheme.id)}
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Badge className={getSchemeTypeBadge(scheme.scheme_type)}>
                                                {getSchemeTypeIcon(scheme.scheme_type)}
                                                <span className="ml-1 capitalize">{scheme.scheme_type}</span>
                                            </Badge>
                                            {scheme.application_deadline && (
                                                <Badge variant="outline" className="flex items-center gap-1">
                                                    <Clock className="h-3 w-3" />
                                                    Deadline: {new Date(scheme.application_deadline).toLocaleDateString()}
                                                </Badge>
                                            )}
                                        </div>

                                        <h3 className="text-lg font-semibold">{scheme.name}</h3>
                                        <p className="text-sm text-muted-foreground mt-1">{scheme.description}</p>

                                        {scheme.benefits && (
                                            <p className="text-sm text-green-700 dark:text-green-400 mt-2 font-medium">
                                                💰 {scheme.benefits}
                                            </p>
                                        )}
                                    </div>

                                    <div className="text-right">
                                        <div className={`text-2xl font-bold ${getMatchScoreColor(scheme.match_score)}`}>
                                            {scheme.match_score}%
                                        </div>
                                        <div className="text-xs text-muted-foreground">match score</div>
                                    </div>
                                </div>
                            </div>

                            {/* Expanded Details */}
                            {expandedScheme === scheme.id && (
                                <div className="border-t bg-muted/50 p-4 space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div>
                                            <div className="text-sm font-medium text-muted-foreground">Max Benefit</div>
                                            <div className="text-lg font-semibold">
                                                {scheme.subsidy_percentage
                                                    ? `${scheme.subsidy_percentage}% subsidy`
                                                    : formatAmount(scheme.max_subsidy_amount)
                                                }
                                            </div>
                                        </div>

                                        <div>
                                            <div className="text-sm font-medium text-muted-foreground">Eligible Crops</div>
                                            <div className="flex flex-wrap gap-1 mt-1">
                                                {scheme.eligible_crops.length > 0
                                                    ? scheme.eligible_crops.map(crop => (
                                                        <Badge key={crop} variant="secondary" className="text-xs">{crop}</Badge>
                                                    ))
                                                    : <span className="text-sm">All crops eligible</span>
                                                }
                                            </div>
                                        </div>

                                        <div>
                                            <div className="text-sm font-medium text-muted-foreground">Eligible States</div>
                                            <div className="flex flex-wrap gap-1 mt-1">
                                                {scheme.eligible_states.length > 0
                                                    ? scheme.eligible_states.slice(0, 3).map(s => (
                                                        <Badge key={s} variant="secondary" className="text-xs">{s}</Badge>
                                                    ))
                                                    : <span className="text-sm">All India</span>
                                                }
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-sm font-medium text-muted-foreground mb-2">Documents Required</div>
                                        <div className="flex flex-wrap gap-2">
                                            {scheme.documents_required.map((doc, i) => (
                                                <div key={i} className="flex items-center gap-1 text-sm bg-card px-2 py-1 rounded border">
                                                    <CheckCircle2 className="h-3 w-3 text-green-500" />
                                                    {doc}
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {scheme.link && (
                                        <Button asChild className="w-full md:w-auto">
                                            <a href={scheme.link} target="_blank" rel="noopener noreferrer">
                                                <ExternalLink className="h-4 w-4 mr-2" />
                                                Apply Now
                                            </a>
                                        </Button>
                                    )}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Tips */}
            {data?.tips && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">💡 Application Tips</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        {data.tips.map((tip, i) => (
                            <div key={i} className="flex items-start gap-2 text-sm">
                                <span>{tip.icon}</span>
                                <span>{tip.text}</span>
                            </div>
                        ))}
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
