// src/context/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode, useRef, useCallback } from "react";
import { useToast } from "@/hooks/use-toast";
import { apiGet, apiPost, setUnauthorizedHandler, API_BASE_URL, authHeaders, invalidateApiCache } from "@/lib/api";
const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

interface User {
    id: number;
    username: string;
    email?: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
    signup: (username: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const { toast } = useToast();

    // Use refs for timers and listeners to avoid stale closures
    const logoutTimerRef = useRef<NodeJS.Timeout | null>(null);
    const isLoggingOutRef = useRef(false);

    const logout = useCallback(async () => {
        // Guard against re-entrant calls (e.g. cascading 401s)
        if (isLoggingOutRef.current) return;
        isLoggingOutRef.current = true;

        const currentToken = token || localStorage.getItem("authToken");

        // Clear local state FIRST so no further API calls use an invalid token
        setToken(null);
        setUser(null);
        localStorage.removeItem("authToken");
        localStorage.removeItem("authUser");
        if (logoutTimerRef.current) clearTimeout(logoutTimerRef.current);
        invalidateApiCache();

        // Best-effort server-side logout using raw fetch to avoid
        // triggering the global 401 handler (which would recurse)
        if (currentToken) {
            try {
                await fetch(`${API_BASE_URL}/logout`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Token ${currentToken}`,
                    },
                    body: JSON.stringify({}),
                });
            } catch { /* best-effort, ignore errors */ }
        }

        isLoggingOutRef.current = false;
    }, [token]);

    // Register global 401 interceptor so API calls auto-logout on expired tokens
    useEffect(() => {
        setUnauthorizedHandler(() => {
            // Skip if already logging out to prevent cascade
            if (isLoggingOutRef.current) return;
            logout();
            toast({
                title: "Session Expired",
                description: "Your session has expired. Please log in again.",
                variant: "destructive",
            });
        });
    }, [logout, toast]);

    const resetTimer = () => {
        if (!token) return;

        if (logoutTimerRef.current) clearTimeout(logoutTimerRef.current);

        logoutTimerRef.current = setTimeout(() => {
            logout();
            toast({
                title: "Session Expired",
                description: "You have been logged out due to inactivity.",
                variant: "destructive",
            });
        }, SESSION_TIMEOUT_MS);
    };

    // Load token from localStorage on mount and validate with server
    useEffect(() => {
        const validateToken = async () => {
            const storedToken = localStorage.getItem("authToken");
            const storedUser = localStorage.getItem("authUser");

            if (storedToken && storedUser) {
                try {
                    // Keep loading true while checking
                    setIsLoading(true);
                    
                    // Manually fetch so we don't use apiGet which relies on global state sometimes, or just use fetch directly
                    const res = await fetch(`${API_BASE_URL}/test_token`, {
                        headers: { "Authorization": `Token ${storedToken}` }
                    });
                    
                    if (res.ok) {
                        setUser(JSON.parse(storedUser));
                        setToken(storedToken);
                    } else {
                        // Invalid token, do silent local cleanup
                        localStorage.removeItem("authToken");
                        localStorage.removeItem("authUser");
                        setToken(null);
                        setUser(null);
                    }
                } catch {
                    // Network error or parse error
                    localStorage.removeItem("authToken");
                    localStorage.removeItem("authUser");
                    setToken(null);
                    setUser(null);
                } finally {
                    setIsLoading(false);
                }
            } else {
                setIsLoading(false);
            }
        };
        
        validateToken();
    }, []);

    // Setup activity listeners when authenticated
    useEffect(() => {
        if (!token) return;

        const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];

        // Initial timer set
        resetTimer();

        // Throttled reset handler
        let lastReset = 0;
        const handleActivity = () => {
            const now = Date.now();
            // Only reset max once every 30 seconds to avoid perf issues
            if (now - lastReset > 30000) {
                resetTimer();
                lastReset = now;
            }
        };

        events.forEach(event => document.addEventListener(event, handleActivity));

        return () => {
            if (logoutTimerRef.current) clearTimeout(logoutTimerRef.current);
            events.forEach(event => document.removeEventListener(event, handleActivity));
        };
    }, [token]);

    const login = async (username: string, password: string): Promise<{ success: boolean; error?: string }> => {
        try {
            const data = await apiPost<{ token: string; user: User }>("/login", { username, password });

            // Store token and user
            setToken(data.token);
            setUser(data.user);
            localStorage.setItem("authToken", data.token);
            localStorage.setItem("authUser", JSON.stringify(data.user));

            return { success: true };
        } catch {
            return { success: false, error: "Network error. Please try again." };
        }
    };

    const signup = async (username: string, email: string, password: string): Promise<{ success: boolean; error?: string }> => {
        try {
            const data = await apiPost<{ token?: string; user?: User; message?: string; email_verification_required?: boolean }>(
                "/signup",
                { username, email, password }
            );

            if (data.email_verification_required) {
                return { success: true };
            }

            if (!data.token || !data.user) {
                return { success: false, error: data.message || "Signup failed" };
            }

            // Auto-login after signup
            setToken(data.token);
            setUser(data.user);
            localStorage.setItem("authToken", data.token);
            localStorage.setItem("authUser", JSON.stringify(data.user));

            return { success: true };
        } catch (error: unknown) {
            const message = error instanceof Error ? error.message : "Network error. Please try again.";
            return { success: false, error: message };
        }
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                isAuthenticated: !!token,
                isLoading,
                login,
                signup,
                logout,
            }}
        >
            {isLoading ? (
                <div className="min-h-screen flex items-center justify-center bg-background">
                    <div className="w-8 h-8 rounded-full border-4 border-l-transparent border-green-600 animate-spin" />
                </div>
            ) : (
                children
            )}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
