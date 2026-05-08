content = """import { Link } from "wouter";
import { useTranslation } from "@/hooks/useTranslation";
import { Language } from "@/lib/translations";

export default function LandingPage() {
    const { t, language, setLanguage } = useTranslation();

    return (
        <div className="bg-landing-bg-light dark:bg-landing-bg-dark text-landing-text-light dark:text-landing-text-dark font-sans antialiased overflow-x-hidden min-h-screen flex flex-col">
            {/* Navigation */}
            <header className="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-800 bg-landing-bg-light/80 dark:bg-landing-bg-dark/80 backdrop-blur-md">
                <div className="px-4 md:px-10 py-4 flex items-center justify-between max-w-[1440px] mx-auto">
                    <div className="flex items-center gap-3">
                        <div className="size-8 text-landing-primary">
                            <span className="material-symbols-outlined text-4xl">agriculture</span>
                        </div>
                        <h2 className="text-xl font-bold tracking-tight text-landing-text-light dark:text-landing-text-dark">AgriSmart</h2>
                    </div>
                    <nav className="hidden md:flex items-center gap-8">
                        <a href="#features" className="text-sm font-medium hover:text-landing-primary transition-colors">{t("lp_btn_learn_more")}</a>
                        <a href="#how-it-works" className="text-sm font-medium hover:text-landing-primary transition-colors">{t("lp_how_title")}</a>
                        <a href="#benefits" className="text-sm font-medium hover:text-landing-primary transition-colors">{t("lp_ben_title")}</a>
                    </nav>
                    <div className="flex items-center gap-4">
                        <select 
                            value={language}
                            onChange={(e) => setLanguage(e.target.value as Language)}
                            className="bg-transparent text-sm font-medium border border-gray-300 dark:border-gray-700 rounded-md px-2 py-1 outline-none focus:ring-2 focus:ring-landing-primary text-landing-text-light dark:text-landing-text-dark cursor-pointer"
                        >
                            <option value="en" className="text-black dark:text-black">English</option>
                            <option value="hi" className="text-black dark:text-black">हिंदी</option>
                            <option value="pa" className="text-black dark:text-black">ਪੰਜਾਬੀ</option>
                            <option value="ml" className="text-black dark:text-black">മലയാളം</option>
                        </select>
                        <Link href="/login" className="hidden sm:block text-sm font-medium hover:text-landing-primary transition-colors">Log In</Link>
                        <Link href="/signup">
                            <button className="flex h-10 px-6 cursor-pointer items-center justify-center rounded-lg bg-landing-primary hover:bg-landing-primary/90 transition-colors text-black text-sm font-bold shadow-lg shadow-landing-primary/20">
                                <span>{t("lp_btn_get_started")}</span>
                            </button>
                        </Link>
                    </div>
                </div>
            </header>

            <main className="flex-1">
                {/* Hero Section */}
                <section className="relative w-full overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-landing-bg-light dark:to-landing-bg-dark z-10"></div>
                    <div
                        className="absolute inset-0 bg-cover bg-center bg-no-repeat z-0 transform scale-105"
                        style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDX7LQwU0BCByxazKzVxG9x7AOIWY6YjKgJ4ENaeGS5MH9xZCDsUnUk7y8bWrQz9eGor2UYGDhxXtpH0x0TtiWORFciEOzZB6xfRERcozagltolI02MgWW32p7ZLdrjRTsPwY0yX38q70wXQUS0bimGtjRVGIK6faggOOLxKUnc2Zxw23Nyge40du2QJjU7WtCVPZWBXH5FBDZKpN2xxCthJM1czZhqnb9on8hY7_6tKZchakCBP8VyBjwo_t5oakk16QxeBdlcSas")' }}
                    >
                    </div>
                    <div className="relative z-20 container mx-auto flex flex-col items-center justify-center min-h-[600px] md:min-h-[700px] px-4 py-20 text-center">
                        <div className="max-w-4xl flex flex-col items-center gap-6 animate-fade-in-up">
                            <div className="inline-flex items-center rounded-full border border-white/20 bg-white/10 px-3 py-1 text-sm font-medium text-white backdrop-blur-md mb-2">
                                <span className="mr-2 flex h-2 w-2 rounded-full bg-landing-primary"></span>
                                {t("lp_hero_badge")}
                            </div>
                            <h1 className="text-4xl md:text-6xl lg:text-7xl font-black text-white leading-tight tracking-tight drop-shadow-sm">
                                {t("lp_hero_title1")}<span className="text-landing-primary">{t("lp_hero_title2")}</span>{t("lp_hero_title3")}
                            </h1>
                            <p className="text-lg md:text-xl text-gray-200 max-w-2xl font-light leading-relaxed">
                                {t("lp_hero_desc")}
                            </p>
                            <div className="flex flex-col sm:flex-row gap-4 mt-4 w-full sm:w-auto">
                                <Link href="/signup">
                                    <button className="h-12 px-8 rounded-lg bg-landing-primary hover:bg-landing-primary/90 text-black text-base font-bold transition-all transform hover:scale-105 shadow-xl shadow-landing-primary/30 w-full sm:w-auto">
                                        {t("lp_btn_get_started")}
                                    </button>
                                </Link>
                                <a href="#features">
                                    <button className="h-12 px-8 rounded-lg bg-white/10 hover:bg-white/20 border border-white/30 backdrop-blur-sm text-white text-base font-bold transition-all w-full sm:w-auto flex items-center justify-center gap-2">
                                        <span className="material-symbols-outlined text-[20px]">arrow_downward</span>
                                        {t("lp_btn_learn_more")}
                                    </button>
                                </a>
                            </div>
                        </div>
                    </div>
                    {/* Curve Separator */}
                    <div className="absolute bottom-0 left-0 right-0 z-20 h-16 bg-landing-bg-light dark:bg-landing-bg-dark" style={{ clipPath: "polygon(0 100%, 100% 100%, 100% 0, 0 100%)" }}></div>
                </section>

                {/* Features Section - Comprehensive list of all modules */}
                <section className="py-20 md:py-32 px-4 md:px-10 max-w-[1440px] mx-auto w-full" id="features">
                    <div className="flex flex-col items-center text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-black text-landing-text-light dark:text-landing-text-dark tracking-tight mb-4 leading-tight">
                            {t("lp_features_title")}
                        </h2>
                        <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed max-w-2xl">
                            {t("lp_features_subtitle")}
                        </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* Feature 1: Satellite Monitoring */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-blue-500 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">satellite_alt</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_feat_sat_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{t("lp_feat_sat_desc")}</p>
                            </div>
                        </div>

                        {/* Feature 2: Pest Detection */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-red-50 dark:bg-red-900/20 flex items-center justify-center text-red-500 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">pest_control</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_feat_pest_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{t("lp_feat_pest_desc")}</p>
                            </div>
                        </div>

                        {/* Feature 3: Financial Ledger */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center text-amber-500 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">account_balance_wallet</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_feat_fin_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{t("lp_feat_fin_desc")}</p>
                            </div>
                        </div>

                        {/* Feature 4: Yield Prediction */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-purple-50 dark:bg-purple-900/20 flex items-center justify-center text-purple-500 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">psychology</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_feat_yield_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{t("lp_feat_yield_desc")}</p>
                            </div>
                        </div>

                        {/* Feature 5: Market Prices & Weather */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-cyan-50 dark:bg-cyan-900/20 flex items-center justify-center text-cyan-500 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">storefront</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_feat_market_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{t("lp_feat_market_desc")}</p>
                            </div>
                        </div>

                        {/* Feature 6: Carbon Credits / AWD */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center text-emerald-500 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">eco</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_feat_awd_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">{t("lp_feat_awd_desc")}</p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* How It Works Section */}
                <section className="py-20 bg-gray-50 dark:bg-[#0c1a0e]/50 relative" id="how-it-works">
                    <div className="px-4 md:px-10 max-w-[1440px] mx-auto">
                        <div className="text-center mb-16">
                            <h2 className="text-3xl md:text-4xl font-black text-landing-text-light dark:text-landing-text-dark mb-4">{t("lp_how_title")}</h2>
                            <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">{t("lp_how_subtitle")}</p>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                            {/* Step 1 */}
                            <div className="relative flex flex-col items-center text-center">
                                <div className="w-16 h-16 rounded-2xl bg-white dark:bg-gray-800 shadow-md flex items-center justify-center mb-6 border border-gray-100 dark:border-gray-700">
                                    <span className="text-xl font-bold text-landing-primary">1</span>
                                </div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_how_1_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm">{t("lp_how_1_desc")}</p>
                            </div>
                            {/* Step 2 */}
                            <div className="relative flex flex-col items-center text-center">
                                <div className="w-16 h-16 rounded-2xl bg-white dark:bg-gray-800 shadow-md flex items-center justify-center mb-6 border border-gray-100 dark:border-gray-700">
                                    <span className="text-xl font-bold text-landing-primary">2</span>
                                </div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_how_2_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm">{t("lp_how_2_desc")}</p>
                            </div>
                            {/* Step 3 */}
                            <div className="relative flex flex-col items-center text-center">
                                <div className="w-16 h-16 rounded-2xl bg-white dark:bg-gray-800 shadow-md flex items-center justify-center mb-6 border border-gray-100 dark:border-gray-700">
                                    <span className="text-xl font-bold text-landing-primary">3</span>
                                </div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_how_3_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm">{t("lp_how_3_desc")}</p>
                            </div>
                            {/* Step 4 */}
                            <div className="relative flex flex-col items-center text-center">
                                <div className="w-16 h-16 rounded-2xl bg-white dark:bg-gray-800 shadow-md flex items-center justify-center mb-6 border border-gray-100 dark:border-gray-700">
                                    <span className="text-xl font-bold text-landing-primary">4</span>
                                </div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">{t("lp_how_4_title")}</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm">{t("lp_how_4_desc")}</p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Benefits Section */}
                <section className="py-20 md:py-32 px-4 md:px-10 max-w-[1440px] mx-auto w-full" id="benefits">
                    <div className="flex flex-col items-center text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-black text-landing-text-light dark:text-landing-text-dark tracking-tight mb-4 leading-tight">
                            {t("lp_ben_title")}
                        </h2>
                        <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed max-w-2xl">
                            {t("lp_ben_subtitle")}
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-900/10 dark:to-green-900/5 p-8 rounded-3xl border border-green-200/50 dark:border-green-800/30 text-center">
                            <span className="material-symbols-outlined text-5xl text-green-600 dark:text-green-400 mb-4 block">trending_up</span>
                            <h3 className="text-2xl font-bold text-landing-text-light dark:text-white mb-3">{t("lp_ben_1_title")}</h3>
                            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{t("lp_ben_1_desc")}</p>
                        </div>
                        <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-900/10 dark:to-blue-900/5 p-8 rounded-3xl border border-blue-200/50 dark:border-blue-800/30 text-center">
                            <span className="material-symbols-outlined text-5xl text-blue-600 dark:text-blue-400 mb-4 block">savings</span>
                            <h3 className="text-2xl font-bold text-landing-text-light dark:text-white mb-3">{t("lp_ben_2_title")}</h3>
                            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{t("lp_ben_2_desc")}</p>
                        </div>
                        <div className="bg-gradient-to-br from-amber-50 to-amber-100/50 dark:from-amber-900/10 dark:to-amber-900/5 p-8 rounded-3xl border border-amber-200/50 dark:border-amber-800/30 text-center">
                            <span className="material-symbols-outlined text-5xl text-amber-600 dark:text-amber-400 mb-4 block">workspace_premium</span>
                            <h3 className="text-2xl font-bold text-landing-text-light dark:text-white mb-3">{t("lp_ben_3_title")}</h3>
                            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{t("lp_ben_3_desc")}</p>
                        </div>
                    </div>
                </section>

                {/* CTA Section */}
                <section className="w-full py-20 bg-landing-bg-light dark:bg-landing-bg-dark">
                    <div className="px-4 md:px-10 max-w-[1440px] mx-auto">
                        <div className="relative overflow-hidden rounded-3xl bg-green-900 px-6 py-16 md:px-16 md:py-24 text-center shadow-2xl">
                            {/* Background Pattern */}
                            <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "radial-gradient(#13ec25 1px, transparent 1px)", backgroundSize: "30px 30px" }}></div>
                            <div className="relative z-10 max-w-3xl mx-auto">
                                <h2 className="text-3xl md:text-5xl font-black text-white mb-6">Ready to maximize your yield?</h2>
                                <p className="text-green-100 text-lg mb-10">Map your fields, monitor crop health with satellite data, and get AI-powered insights — all in one platform.</p>
                                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                                    <Link href="/signup">
                                        <button className="h-12 px-8 rounded-lg bg-landing-primary hover:bg-landing-primary/90 text-black text-base font-bold transition-all shadow-lg shadow-green-900/50">
                                            {t("lp_btn_get_started")}
                                        </button>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            {/* Footer */}
            <footer className="bg-white dark:bg-black border-t border-gray-200 dark:border-gray-900 pt-16 pb-8">
                <div className="px-4 md:px-10 max-w-[1440px] mx-auto text-center">
                    <div className="flex items-center justify-center gap-2 mb-6">
                        <span className="material-symbols-outlined text-3xl text-landing-primary">agriculture</span>
                        <span className="text-xl font-bold text-landing-text-light dark:text-landing-text-dark">AgriSmart</span>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mb-6 max-w-md mx-auto">
                        Empowering farmers worldwide with data-driven insights for sustainable and profitable agriculture.
                    </p>
                    <div className="border-t border-gray-100 dark:border-gray-800 pt-8 flex flex-col justify-center items-center gap-4 text-xs text-gray-500 dark:text-gray-500">
                        <p>© 2026 AgriSmart Inc. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
"""

with open("client/src/pages/LandingPage.tsx", "w", encoding="utf-8") as f:
    f.write(content)
