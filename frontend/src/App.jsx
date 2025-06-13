import { createBrowserRouter, RouterProvider } from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import SignupPage from "@/routes/signup/page";
import LoginPage from "@/routes/login/page";
import DashboardPage from "@/routes/dashboard/page";

import { AuthProvider } from "@/providers/auth-provider";

import { Toaster } from "@/components/ui/sonner";
import { ProtectedRoute } from "@/components/protected-route";
import { RedircetToDashboard } from "@/components/redirect-to-dashboard";

const queryClient = new QueryClient();

function App() {
    const router = createBrowserRouter([
        {
            path: "/",
            element: (
                <ProtectedRoute>
                    <DashboardPage />
                </ProtectedRoute>
            ),
        },
        {
            path: "/signup",
            element: (
                <RedircetToDashboard>
                    <SignupPage />
                </RedircetToDashboard>
            ),
        },
        {
            path: "/login",
            element: (
                <RedircetToDashboard>
                    <LoginPage />
                </RedircetToDashboard>
            ),
        },
    ]);

    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <RouterProvider router={router} />
            </AuthProvider>
            <Toaster richColors />
        </QueryClientProvider>
    );
}

export default App;
