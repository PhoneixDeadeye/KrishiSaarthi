import { useState } from "react";
import { Link, useLocation, useRoute } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Sprout, Loader2, Eye, EyeOff, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiPost } from "@/lib/api";

export default function ResetPassword() {
    const [, setLocation] = useLocation();
    const [match, params] = useRoute("/reset-password/:uid/:token");
    const { toast } = useToast();

    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!password || !confirmPassword) {
            toast({ variant: "destructive", title: "Error", description: "Please fill in all fields" });
            return;
        }

        if (password !== confirmPassword) {
            toast({ variant: "destructive", title: "Error", description: "Passwords do not match" });
            return;
        }

        if (password.length < 8) {
            toast({ variant: "destructive", title: "Error", description: "Password must be at least 8 characters" });
            return;
        }

        if (!match || !params) {
            toast({ variant: "destructive", title: "Error", description: "Invalid password reset link" });
            return;
        }

        setIsLoading(true);
        try {
            await apiPost('/password-reset-confirm', {
                uidb64: params.uid,
                token: params.token,
                password: password
            });

            setIsSuccess(true);
            toast({ title: "Success", description: "Your password has been reset successfully." });
        } catch (error: any) {
            toast({
                variant: "destructive",
                title: "Error",
                description: error.message || "Invalid or expired token"
            });
        } finally {
            setIsLoading(false);
        }
    };

    if (!match) {
        return <div className="p-4 text-center">Invalid Link</div>;
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 p-4">
            <Card className="w-full max-w-md shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader className="text-center space-y-4">
                    <div className="mx-auto w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
                        <Sprout className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <CardTitle className="text-2xl font-bold text-gray-800">Set New Password</CardTitle>
                        <CardDescription className="text-gray-600">
                            Create a strong password for your account
                        </CardDescription>
                    </div>
                </CardHeader>

                <CardContent>
                    {isSuccess ? (
                        <div className="text-center space-y-6">
                            <div className="flex flex-col items-center justify-center text-green-600 space-y-2">
                                <CheckCircle className="w-16 h-16" />
                                <h3 className="text-xl font-semibold">Password Reset Complete!</h3>
                                <p className="text-sm text-gray-600">You can now sign in with your new password.</p>
                            </div>
                            <Button
                                className="w-full h-11 bg-gradient-to-r from-green-500 to-emerald-600 text-white"
                                onClick={() => setLocation("/login")}
                            >
                                Continue to Login
                            </Button>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700">New Password</label>
                                <div className="relative">
                                    <Input
                                        type={showPassword ? "text" : "password"}
                                        placeholder="••••••••"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        disabled={isLoading}
                                        className="h-11 pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                    >
                                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700">Confirm Password</label>
                                <Input
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    disabled={isLoading}
                                    className="h-11"
                                />
                            </div>

                            <Button
                                type="submit"
                                disabled={isLoading}
                                className="w-full h-11 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-medium"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Resetting...
                                    </>
                                ) : (
                                    "Reset Password"
                                )}
                            </Button>
                        </form>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
