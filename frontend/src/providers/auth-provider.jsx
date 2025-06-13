import { createContext, useContext } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Cookies from "js-cookie";
import { axiosInstance } from "@/utils/axios-instance";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const queryClient = useQueryClient();

    const {
        data: user,
        isLoading: isAuthenticating,
        isSuccess,
    } = useQuery({
        queryKey: ["auth"],
        queryFn: async () => {
            const response = await axiosInstance.get("/auth/me");
            return response.data.data;
        },
        retry: false,
        refetchOnWindowFocus: false,
    });

    const { mutateAsync: logout } = useMutation({
        mutationFn: async () => {
            Cookies.remove("token");
            await queryClient.cancelQueries();
            queryClient.clear();
        },
    });

    const isAuthenticated = !!user && isSuccess;

    return <AuthContext value={{ isAuthenticating, isAuthenticated, logout }}>{children}</AuthContext>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
