"use client"
import { useRouter } from "next/navigation";

export default function Page() {
    const router = useRouter();

    function handleSubmit(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const roomcode = formData.get('roomcode');

        router.push('/ytclient/player');
    }

    return (
        <form method="post" onSubmit={handleSubmit} className="center-container">
            <label>
                Room Code: <input name="roomcode" placeholder="Enter your room code here" />
            </label>
            <button type="submit">Submit form</button>
        </form>
    );
}
