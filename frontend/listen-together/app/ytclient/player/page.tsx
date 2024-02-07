"use client"
import YTPlayer from "@/app/players/YTPlayer";
import { useRouter} from "next/navigation";

export default function Page() {
    const router = useRouter();
    const { roomcode } = router.query;
    console.log(roomcode);

    return (
        <YTPlayer/>
    )
}