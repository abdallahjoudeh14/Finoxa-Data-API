import { useState } from "react";
import { toast } from "sonner";
import { Link, useNavigate } from "react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { axiosInstance } from "@/utils/axios-instance";

import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardDescription, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import Cookies from "js-cookie";

const SignupPage = () => {
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    const { mutate: signup, isPending: isSigning } = useMutation({
        mutationFn: async (user) => {
            const response = await axiosInstance.post("/auth/signup", user);
            return response.data;
        },
        onSuccess: (user) => {
            Cookies.set("token", user.access_token, {
                secure: true,
                sameSite: "none",
                expires: new Date(new Date().getTime() + import.meta.env.VITE_ACCESS_TOKEN_EXPIRATION_TIME * 60 * 1000),
            });
            queryClient.setQueryData(["auth"], user);
            toast.success("Signed up successfully");
            navigate("/", { replace: true });
        },
        onError: (error) => {
            toast.error(error.response.data.message);
        },
    });

    const [user, setUser] = useState({
        name: "",
        email: "",
        password: "",
    });

    const handleChange = (event) => {
        const { name, value } = event.target;
        setUser((prevUser) => ({ ...prevUser, [name]: value }));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        signup(user);
    };

    return (
        <div className="flex min-h-screen items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle className="text-2xl">Create an account</CardTitle>
                    <CardDescription>Enter your information to create a new account</CardDescription>
                </CardHeader>
                <form
                    className="grid gap-y-4"
                    onSubmit={handleSubmit}
                >
                    <CardContent className="grid gap-y-4">
                        <div className="grid gap-y-2">
                            <Label htmlFor="fullName">Full name</Label>
                            <Input
                                id="fullName"
                                name="name"
                                placeholder="Enter your full name"
                                value={user.name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="grid gap-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                name="email"
                                placeholder="Enter your email"
                                value={user.email}
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
                                value={user.password}
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
                            disabled={isSigning}
                        >
                            {isSigning ? "Signing up..." : "Sign up"}
                        </Button>
                        <div className="text-center text-sm">
                            Already have an account?{" "}
                            <Link
                                to="/login"
                                className="text-primary hover:underline underline-offset-4"
                            >
                                Log in
                            </Link>
                        </div>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
};

export default SignupPage;
