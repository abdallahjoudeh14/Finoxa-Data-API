import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Cookies from "js-cookie";
import { toast } from "sonner";

import { axiosInstance } from "@/utils/axios-instance";

import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardDescription, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";

const LoginPage = () => {
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    const [inputValues, setInputValues] = useState({
        email: "",
        password: "",
    });

    const { mutate: login, isPending: isLogging } = useMutation({
        mutationFn: async (user) => {
            const response = await axiosInstance.post("/auth/login", user);
            return response.data;
        },
        onSuccess: (user) => {
            Cookies.set("token", user.access_token, {
                secure: true,
                sameSite: "none",
                expires: new Date(new Date().getTime() + import.meta.env.VITE_ACCESS_TOKEN_EXPIRATION_TIME * 60 * 1000),
            });
            queryClient.setQueryData(["auth"], user);
            toast.success("Logged in successfully");
            navigate("/", { replace: true });
        },
        onError: (error) => {
            toast.error(error.response.data.message);
        },
    });

    const handleChange = (event) => {
        const { name, value } = event.target;
        setInputValues((prevUser) => ({ ...prevUser, [name]: value }));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        login(inputValues);
    };

    return (
        <div className="flex min-h-screen items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle className="text-2xl">Log in</CardTitle>
                    <CardDescription>Enter your credentials to access your account</CardDescription>
                </CardHeader>
                <form
                    className="grid gap-y-4"
                    onSubmit={handleSubmit}
                >
                    <CardContent className="grid gap-y-4">
                        <div className="grid gap-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                name="email"
                                placeholder="Enter your email"
                                value={inputValues.email}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="grid gap-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                name="password"
                                type="password"
                                value={inputValues.password}
                                onChange={handleChange}
                                required
                                minLength={6}
                                placeholder="Enter your password"
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex flex-col space-y-4">
                        <Button
                            type="submit"
                            className="w-full cursor-pointer"
                            disabled={isLogging}
                        >
                            {isLogging ? "Logging in..." : "Log in"}
                        </Button>
                        <div className="text-center text-sm">
                            Don't have an account?{" "}
                            <Link
                                to="/signup"
                                className="text-primary hover:underline underline-offset-4"
                            >
                                Sign up
                            </Link>
                        </div>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
};

export default LoginPage;
