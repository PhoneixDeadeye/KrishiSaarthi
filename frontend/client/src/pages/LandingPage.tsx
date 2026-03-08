import { Link } from "wouter";

export default function LandingPage() {

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
                        <a href="#features" className="text-sm font-medium hover:text-landing-primary transition-colors">Features</a>
                        <a href="#how-it-works" className="text-sm font-medium hover:text-landing-primary transition-colors">How it Works</a>
                        <a href="#use-cases" className="text-sm font-medium hover:text-landing-primary transition-colors">Use Cases</a>
                    </nav>
                    <div className="flex items-center gap-4">
                        <Link href="/login" className="hidden sm:block text-sm font-medium hover:text-landing-primary transition-colors">Log In</Link>
                        <Link href="/signup">
                            <button className="flex h-10 px-6 cursor-pointer items-center justify-center rounded-lg bg-landing-primary hover:bg-landing-primary/90 transition-colors text-black text-sm font-bold shadow-lg shadow-landing-primary/20">
                                <span>Get Started</span>
                            </button>
                        </Link>
                    </div>
                </div>
            </header>

            <main className="flex-1">
                {/* Hero Section */}
                <section className="relative w-full overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/20 to-landing-bg-light dark:to-landing-bg-dark z-10"></div>
                    <div
                        className="absolute inset-0 bg-cover bg-center bg-no-repeat z-0 transform scale-105"
                        style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDX7LQwU0BCByxazKzVxG9x7AOIWY6YjKgJ4ENaeGS5MH9xZCDsUnUk7y8bWrQz9eGor2UYGDhxXtpH0x0TtiWORFciEOzZB6xfRERcozagltolI02MgWW32p7ZLdrjRTsPwY0yX38q70wXQUS0bimGtjRVGIK6faggOOLxKUnc2Zxw23Nyge40du2QJjU7WtCVPZWBXH5FBDZKpN2xxCthJM1czZhqnb9on8hY7_6tKZchakCBP8VyBjwo_t5oakk16QxeBdlcSas")' }}
                    >
                    </div>
                    <div className="relative z-20 container mx-auto flex flex-col items-center justify-center min-h-[600px] md:min-h-[700px] px-4 py-20 text-center">
                        <div className="max-w-4xl flex flex-col items-center gap-6 animate-fade-in-up">
                            <div className="inline-flex items-center rounded-full border border-white/20 bg-white/10 px-3 py-1 text-sm font-medium text-white backdrop-blur-md mb-2">
                                <span className="mr-2 flex h-2 w-2 rounded-full bg-landing-primary"></span>
                                Satellite-Powered Farm Intelligence
                            </div>
                            <h1 className="text-4xl md:text-6xl lg:text-7xl font-black text-white leading-tight tracking-tight drop-shadow-sm">
                                Empowering the <span className="text-landing-primary">Future</span> of Farming
                            </h1>
                            <p className="text-lg md:text-xl text-gray-200 max-w-2xl font-light leading-relaxed">
                                Leverage real-time satellite imagery and AI-driven insights to maximize yield, minimize waste, and cultivate a smarter future for your farm.
                            </p>
                            <div className="flex flex-col sm:flex-row gap-4 mt-4 w-full sm:w-auto">
                                <Link href="/signup">
                                    <button className="h-12 px-8 rounded-lg bg-landing-primary hover:bg-landing-primary/90 text-black text-base font-bold transition-all transform hover:scale-105 shadow-xl shadow-landing-primary/30 w-full sm:w-auto">
                                        Get Started Free
                                    </button>
                                </Link>
                                <a href="#features">
                                    <button className="h-12 px-8 rounded-lg bg-white/10 hover:bg-white/20 border border-white/30 backdrop-blur-sm text-white text-base font-bold transition-all w-full sm:w-auto flex items-center justify-center gap-2">
                                        <span className="material-symbols-outlined text-[20px]">arrow_downward</span>
                                        Learn More
                                    </button>
                                </a>
                            </div>
                        </div>
                    </div>
                    {/* Curve Separator */}
                    <div className="absolute bottom-0 left-0 right-0 z-20 h-16 bg-landing-bg-light dark:bg-landing-bg-dark" style={{ clipPath: "polygon(0 100%, 100% 100%, 100% 0, 0 100%)" }}></div>
                </section>

                {/* Features Section */}
                <section className="py-20 md:py-32 px-4 md:px-10 max-w-[1440px] mx-auto w-full" id="features">
                    <div className="flex flex-col md:flex-row gap-12 items-start justify-between mb-16">
                        <div className="max-w-xl">
                            <h2 className="text-3xl md:text-5xl font-black text-landing-text-light dark:text-landing-text-dark tracking-tight mb-4 leading-tight">
                                Cultivating <br /><span className="text-transparent bg-clip-text bg-gradient-to-r from-landing-primary to-green-600">Intelligence</span>
                            </h2>
                            <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
                                Our platform provides comprehensive tools to monitor and optimize every aspect of your farm, from the soil up to the satellite view.
                            </p>
                        </div>
                        <div className="flex items-end">
                            <a href="#" className="group flex items-center gap-2 text-landing-primary font-bold hover:underline">
                                View all features
                                <span className="material-symbols-outlined transition-transform group-hover:translate-x-1">arrow_forward</span>
                            </a>
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {/* Feature 1 */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center text-landing-primary group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">eco</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Crop Health</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Monitor plant vitality with NDVI satellite imagery and detect stress before it spreads.</p>
                            </div>
                        </div>
                        {/* Feature 2 */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center text-landing-primary group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">monitoring</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Market Prices</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Reference MSP and indicative commodity prices to help plan your selling strategy.</p>
                            </div>
                        </div>
                        {/* Feature 3 */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center text-landing-primary group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">smart_toy</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">AI Chat Assistant</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Get instant, personalized farming advice powered by Gemini AI, available 24/7 in your language.</p>
                            </div>
                        </div>
                        {/* Feature 4 */}
                        <div className="group flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-white/5 p-6 hover:shadow-xl hover:shadow-landing-primary/5 hover:border-landing-primary/50 transition-all duration-300">
                            <div className="size-12 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center text-landing-primary group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined text-3xl">psychology</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Yield Prediction</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">AI-driven forecasts that analyze historical data for better harvest planning.</p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* How It Works Section */}
                <section className="py-20 bg-white dark:bg-[#0c1a0e] relative" id="how-it-works">
                    <div className="px-4 md:px-10 max-w-[1440px] mx-auto">
                        <div className="text-center mb-16">
                            <h2 className="text-3xl md:text-4xl font-black text-landing-text-light dark:text-landing-text-dark mb-4">Streamlined for Success</h2>
                            <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">From setup to harvest, AgriSmart integrates seamlessly into your workflow in three simple steps.</p>
                        </div>
                        <div className="relative grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
                            {/* Connecting Line (Desktop) */}
                            <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-0.5 bg-gradient-to-r from-gray-200 via-landing-primary to-gray-200 dark:from-gray-800 dark:via-landing-primary dark:to-gray-800 z-0"></div>
                            {/* Step 1 */}
                            <div className="relative z-10 flex flex-col items-center text-center group">
                                <div className="w-24 h-24 rounded-full bg-landing-bg-light dark:bg-landing-bg-dark border-4 border-white dark:border-[#0c1a0e] shadow-lg flex items-center justify-center mb-6 group-hover:scale-105 transition-transform duration-300">
                                    <span className="material-symbols-outlined text-4xl text-landing-primary">map</span>
                                </div>
                                <div className="bg-gray-50 dark:bg-white/5 p-6 rounded-2xl w-full border border-gray-100 dark:border-gray-800">
                                    <div className="inline-block px-3 py-1 bg-landing-primary/10 text-landing-primary text-xs font-bold rounded-full mb-3">STEP 01</div>
                                    <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Map Your Fields</h3>
                                    <p className="text-gray-500 dark:text-gray-400 text-sm">Draw your field boundaries on an interactive map. Our system auto-calculates area and links to satellite data.</p>
                                </div>
                            </div>
                            {/* Step 2 */}
                            <div className="relative z-10 flex flex-col items-center text-center group">
                                <div className="w-24 h-24 rounded-full bg-landing-bg-light dark:bg-landing-bg-dark border-4 border-white dark:border-[#0c1a0e] shadow-lg flex items-center justify-center mb-6 group-hover:scale-105 transition-transform duration-300">
                                    <span className="material-symbols-outlined text-4xl text-landing-primary">analytics</span>
                                </div>
                                <div className="bg-gray-50 dark:bg-white/5 p-6 rounded-2xl w-full border border-gray-100 dark:border-gray-800">
                                    <div className="inline-block px-3 py-1 bg-landing-primary/10 text-landing-primary text-xs font-bold rounded-full mb-3">STEP 02</div>
                                    <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Analyze Data</h3>
                                    <p className="text-gray-500 dark:text-gray-400 text-sm">AI algorithms process soil, weather, and crop data to identify patterns and risks.</p>
                                </div>
                            </div>
                            {/* Step 3 */}
                            <div className="relative z-10 flex flex-col items-center text-center group">
                                <div className="w-24 h-24 rounded-full bg-landing-bg-light dark:bg-landing-bg-dark border-4 border-white dark:border-[#0c1a0e] shadow-lg flex items-center justify-center mb-6 group-hover:scale-105 transition-transform duration-300">
                                    <span className="material-symbols-outlined text-4xl text-landing-primary">rocket_launch</span>
                                </div>
                                <div className="bg-gray-50 dark:bg-white/5 p-6 rounded-2xl w-full border border-gray-100 dark:border-gray-800">
                                    <div className="inline-block px-3 py-1 bg-landing-primary/10 text-landing-primary text-xs font-bold rounded-full mb-3">STEP 03</div>
                                    <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Optimize Harvest</h3>
                                    <p className="text-gray-500 dark:text-gray-400 text-sm">Receive actionable alerts and execute precise interventions to boost your ROI.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Testimonials Section */}
                {/* Use Cases Section */}
                <section className="py-20 md:py-32 px-4 md:px-10 max-w-[1440px] mx-auto w-full" id="use-cases">
                    <h2 className="text-3xl md:text-4xl font-black text-center text-landing-text-light dark:text-landing-text-dark mb-4">Built for Real Farming Workflows</h2>
                    <p className="text-center text-gray-500 dark:text-gray-400 mb-16 max-w-2xl mx-auto">See how AgriSmart helps farmers at every stage of the growing season.</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="flex flex-col p-8 rounded-2xl bg-white dark:bg-white/5 border border-gray-200 dark:border-gray-800 shadow-sm">
                            <div className="size-12 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-blue-500 mb-4">
                                <span className="material-symbols-outlined text-3xl">satellite_alt</span>
                            </div>
                            <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Satellite Monitoring</h3>
                            <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Track NDVI vegetation indices over time using Google Earth Engine. Spot stressed zones before visible damage occurs and take targeted action.</p>
                        </div>
                        <div className="flex flex-col p-8 rounded-2xl bg-white dark:bg-white/5 border border-gray-200 dark:border-gray-800 shadow-sm">
                            <div className="size-12 rounded-lg bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center text-amber-500 mb-4">
                                <span className="material-symbols-outlined text-3xl">account_balance_wallet</span>
                            </div>
                            <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Financial Planning</h3>
                            <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Log income, expenses, and harvest sales. Get a clear financial overview of your farm operations with category breakdowns and trends.</p>
                        </div>
                        <div className="flex flex-col p-8 rounded-2xl bg-white dark:bg-white/5 border border-gray-200 dark:border-gray-800 shadow-sm">
                            <div className="size-12 rounded-lg bg-red-50 dark:bg-red-900/20 flex items-center justify-center text-red-500 mb-4">
                                <span className="material-symbols-outlined text-3xl">pest_control</span>
                            </div>
                            <h3 className="text-xl font-bold text-landing-text-light dark:text-white mb-2">Pest Detection</h3>
                            <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">Upload a photo of affected crops and our CNN model identifies the disease. Get AI-powered treatment recommendations instantly.</p>
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
                                            Create Free Account
                                        </button>
                                    </Link>
                                    <Link href="/login">
                                        <button className="h-12 px-8 rounded-lg bg-transparent border border-white/30 text-white hover:bg-white/10 text-base font-bold transition-all">
                                            Log In
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
                <div className="px-4 md:px-10 max-w-[1440px] mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 mb-16">
                        <div className="lg:col-span-2">
                            <div className="flex items-center gap-2 mb-6">
                                <span className="material-symbols-outlined text-3xl text-landing-primary">agriculture</span>
                                <span className="text-xl font-bold text-landing-text-light dark:text-landing-text-dark">AgriSmart</span>
                            </div>
                            <p className="text-gray-500 dark:text-gray-400 text-sm mb-6 max-w-xs">
                                Empowering farmers worldwide with data-driven insights for sustainable and profitable agriculture.
                            </p>
                            <div className="flex gap-4">
                                <a href="#" className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-600 dark:text-gray-400 hover:bg-landing-primary hover:text-black transition-colors">
                                    <svg aria-hidden="true" className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"></path></svg>
                                </a>
                                <a href="#" className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-600 dark:text-gray-400 hover:bg-landing-primary hover:text-black transition-colors">
                                    <svg aria-hidden="true" className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path clipRule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.468 2.37c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.882-.344-1.857-.047-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" fillRule="evenodd"></path></svg>
                                </a>
                                <a href="#" className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-600 dark:text-gray-400 hover:bg-landing-primary hover:text-black transition-colors">
                                    <svg aria-hidden="true" className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" fillRule="evenodd"></path></svg>
                                </a>
                            </div>
                        </div>
                        <div>
                            <h4 className="font-bold text-landing-text-light dark:text-white mb-4">Product</h4>
                            <ul className="flex flex-col gap-3 text-sm text-gray-500 dark:text-gray-400">
                                <li><a href="#features" className="hover:text-landing-primary transition-colors">Features</a></li>
                                <li><a href="#how-it-works" className="hover:text-landing-primary transition-colors">How it Works</a></li>
                                <li><a href="#use-cases" className="hover:text-landing-primary transition-colors">Use Cases</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-bold text-landing-text-light dark:text-white mb-4">Company</h4>
                            <ul className="flex flex-col gap-3 text-sm text-gray-500 dark:text-gray-400">
                                <li><Link href="/signup" className="hover:text-landing-primary transition-colors">Sign Up</Link></li>
                                <li><Link href="/login" className="hover:text-landing-primary transition-colors">Log In</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-bold text-landing-text-light dark:text-white mb-4">Get Started</h4>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">Create an account to start monitoring your fields with satellite data and AI insights.</p>
                            <Link href="/signup">
                                <button className="h-10 w-full rounded-md bg-landing-primary hover:bg-landing-primary/90 text-black text-sm font-bold transition-colors">Sign Up Free</button>
                            </Link>
                        </div>
                    </div>
                    <div className="border-t border-gray-100 dark:border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-gray-500 dark:text-gray-500">
                        <p>© 2026 AgriSmart Inc. All rights reserved.</p>
                        <div className="flex gap-6">
                            <a href="#" className="hover:text-landing-text-light dark:hover:text-white transition-colors">Privacy Policy</a>
                            <a href="#" className="hover:text-landing-text-light dark:hover:text-white transition-colors">Terms of Service</a>
                            <a href="#" className="hover:text-landing-text-light dark:hover:text-white transition-colors">Cookie Settings</a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
