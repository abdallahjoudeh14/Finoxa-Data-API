import { Navigate } from "react-router";

import { useAuth } from "@/providers/auth-provider";

import { LoaderCircleIcon } from "lucide-react";

export const ProtectedRoute = ({ children }) => {
    const { isAuthenticating, isAuthenticated } = useAuth();

    if (isAuthenticating) {
        return (
            <div className="w-screen h-screen flex justify-center items-center">
                <LoaderCircleIcon className="text-primary animate-spin" />
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }

    return children;
};
