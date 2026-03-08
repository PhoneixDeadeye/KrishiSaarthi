// src/pages/LoginPage.tsx
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
    const [, setLocation] = useLocation();
    const { login, isAuthenticated } = useAuth();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    // Redirect if already authenticated (using useEffect to avoid state update during render)
    useEffect(() => {
        if (isAuthenticated) {
            setLocation("/dashboard");
        }
    }, [isAuthenticated, setLocation]);

    if (isAuthenticated) {
        return null;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (!username.trim() || !password.trim()) {
            setError("Please fill in all fields");
            return;
        }

        setIsLoading(true);
        const result = await login(username, password);
        setIsLoading(false);

        if (result.success) {
            setLocation("/dashboard");
        } else {
            setError(result.error || "Login failed");
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* Left Panel - Branding */}
            <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary via-primary/90 to-primary/80 relative overflow-hidden">
                {/* Decorative Elements */}
                <div className="absolute inset-0">
                    <div className="absolute top-20 left-20 size-64 bg-white/10 rounded-full blur-3xl" />
                    <div className="absolute bottom-20 right-20 size-48 bg-white/10 rounded-full blur-3xl" />
                </div>

                <div className="relative z-10 flex flex-col justify-center p-12 text-white">
                    <div className="mb-8">
                        <div className="size-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mb-6">
                            <span className="material-symbols-outlined text-3xl">eco</span>
                        </div>
                        <h1 className="text-4xl font-bold mb-4">AgriSmart</h1>
                        <p className="text-xl text-white/80">Your Smart Farming Companion</p>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center gap-3 text-white/90">
                            <span className="material-symbols-outlined">check_circle</span>
                            <span>AI-powered crop monitoring</span>
                        </div>
                        <div className="flex items-center gap-3 text-white/90">
                            <span className="material-symbols-outlined">check_circle</span>
                            <span>Real-time weather insights</span>
                        </div>
                        <div className="flex items-center gap-3 text-white/90">
                            <span className="material-symbols-outlined">check_circle</span>
                            <span>Smart irrigation scheduling</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Panel - Form */}
            <div className="flex-1 flex items-center justify-center p-6 bg-background">
                <div className="w-full max-w-md">
                    {/* Mobile Logo */}
                    <div className="lg:hidden text-center mb-8">
                        <div className="size-14 bg-primary rounded-xl flex items-center justify-center mx-auto mb-4">
                            <span className="material-symbols-outlined text-2xl text-white">eco</span>
                        </div>
                        <h2 className="text-2xl font-bold">AgriSmart</h2>
                    </div>

                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-bold">Welcome Back</h2>
                        <p className="text-muted-foreground mt-1">Sign in to your account</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div className="p-3 text-sm text-red-600 bg-red-500/10 rounded-lg border border-red-500/20 flex items-center gap-2">
                                <span className="material-symbols-outlined text-lg">error</span>
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Username</label>
                            <div className="relative">
                                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">person</span>
                                <Input
                                    type="text"
                                    placeholder="Enter your username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    disabled={isLoading}
                                    className="h-12 pl-10 bg-muted/50"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Password</label>
                            <div className="relative">
                                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">lock</span>
                                <Input
                                    type={showPassword ? "text" : "password"}
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={isLoading}
                                    className="h-12 pl-10 pr-10 bg-muted/50"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                                >
                                    <span className="material-symbols-outlined">{showPassword ? "visibility_off" : "visibility"}</span>
                                </button>
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <button
                                type="button"
                                onClick={() => setLocation("/forgot-password")}
                                className="text-sm font-medium text-primary hover:underline"
                            >
                                Forgot password?
                            </button>
                        </div>

                        <Button type="submit" disabled={isLoading} className="w-full h-12 gap-2">
                            {isLoading ? (
                                <>
                                    <span className="material-symbols-outlined animate-spin">progress_activity</span>
                                    Signing in...
                                </>
                            ) : (
                                <>
                                    <span className="material-symbols-outlined">login</span>
                                    Sign In
                                </>
                            )}
                        </Button>
                    </form>

                    <div className="mt-8 text-center text-sm text-muted-foreground">
                        Don't have an account?{" "}
                        <button
                            onClick={() => setLocation("/signup")}
                            className="text-primary font-medium hover:underline"
                        >
                            Sign up
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
