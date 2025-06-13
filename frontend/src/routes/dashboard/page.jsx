import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { axiosInstance } from "@/utils/axios-instance";

import { Header } from "@/components/layouts/header";
import { Button } from "@/components/ui/button";

import { CopyCheckIcon, CopyIcon, LoaderCircleIcon, PlusCircleIcon, RefreshCwIcon, Trash2Icon } from "lucide-react";

const DashboardPage = () => {
    const [isCopying, setIsCopying] = useState(false);

    const {
        data: user,
        refetch: getUser,
        isLoading,
    } = useQuery({
        queryKey: ["user"],
        queryFn: async () => {
            const response = await axiosInstance.get("/user");
            return response.data.data;
        },
        retry: false,
        refetchOnWindowFocus: false,
    });

    const { mutate: generateAPIKey, isPending: isGenerating } = useMutation({
        mutationFn: async () => {
            const response = await axiosInstance.put("/user/generate-apikey");
            await getUser();
            return response.data;
        },
    });

    const { mutate: deleteAPIKey, isPending: isDeleting } = useMutation({
        mutationKey: ["delete-apikey"],
        mutationFn: async () => {
            const response = await axiosInstance.delete("/user/delete-apikey");
            await getUser();
            return response.data;
        },
    });

    const handleCopyKey = (apiKey) => {
        setIsCopying(true);
        navigator.clipboard.writeText(apiKey);
        setTimeout(() => {
            setIsCopying(false);
        }, 1000);
    };

    if (isLoading) {
        return (
            <div className="w-screen h-screen flex justify-center items-center">
                <LoaderCircleIcon className="text-primary animate-spin" />
            </div>
        );
    }
    return (
        <div className="min-h-screen">
            <Header />
            <main className="container pt-16">
                <div className="flex justify-between items-center flex-wrap gap-4">
                    <div>
                        <h1 className="text-2xl font-bold">API Keys</h1>
                        <p className="text-muted-foreground">Manage your API keys to authenticate with our services.</p>
                    </div>
                    <Button
                        className="cursor-pointer"
                        disabled={user?.api_key || isGenerating}
                        onClick={generateAPIKey}
                    >
                        {isGenerating && !user?.api_key ? <LoaderCircleIcon className="animate-spin" /> : <PlusCircleIcon />}
                        <span>New Key</span>
                    </Button>
                </div>
                <div className="mt-10">
                    <div className="border rounded-md p-4 flex flex-col gap-4">
                        <div>
                            <p className="font-medium">Key</p>
                        </div>
                        {user?.api_key ? (
                            <div className="flex items-center justify-between gap-4">
                                <p className="text-muted-foreground overflow-ellipsis overflow-hidden max-w-52">{user?.api_key}</p>
                                <div className="flex items-center gap-2">
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        className="cursor-pointer"
                                        onClick={() => handleCopyKey(user?.api_key)}
                                        disabled={isCopying}
                                    >
                                        {!isCopying ? <CopyIcon /> : <CopyCheckIcon />}
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        className="group cursor-pointer"
                                        onClick={generateAPIKey}
                                        disabled={isGenerating}
                                    >
                                        <RefreshCwIcon className="group-disabled:animate-spin" />
                                    </Button>
                                    <Button
                                        variant="destructive"
                                        size="icon"
                                        className="cursor-pointer"
                                        onClick={deleteAPIKey}
                                        disabled={isDeleting}
                                    >
                                        {isDeleting ? <LoaderCircleIcon className="animate-spin" /> : <Trash2Icon />}
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center">
                                <p>You have not generated any API keys yet.</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default DashboardPage;
