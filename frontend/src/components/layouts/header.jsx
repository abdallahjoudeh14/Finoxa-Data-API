import { useNavigate } from "react-router";

import { useAuth } from "@/providers/auth-provider";

import { Button } from "../ui/button";
import { ArrowUpRightIcon } from "lucide-react";

import FinoxaLogo from "@/assets/Finoxa-icon.svg";

export const Header = () => {
    const navigate = useNavigate();
    const { logout } = useAuth();

    const handleLogout = async () => {
        try {
            await logout();
            navigate("/login", { replace: true });
        } catch (err) {
            console.error("Logout failed:", err.message);
        }
    };

    return (
        <header className="container">
            <div className="flex justify-between py-4 flex-wrap">
                <div className="flex items-center gap-2">
                    <img
                        src={FinoxaLogo}
                        alt="Finoxa Logo"
                        className="h-6 w-auto"
                    />
                    <p className="text-lg font-medium">Finoxa API</p>
                </div>
                <div>
                    <Button
                        asChild
                        variant="link"
                        className="cursor-pointer"
                    >
                        <a
                            href="https://finoxa-api.apidog.io/"
                            target="_blank"
                        >
                            Docs
                            <ArrowUpRightIcon />
                        </a>
                    </Button>
                    <Button
                        className="cursor-pointer"
                        size="sm"
                        onClick={handleLogout}
                    >
                        Logout
                    </Button>
                </div>
            </div>
        </header>
    );
};
