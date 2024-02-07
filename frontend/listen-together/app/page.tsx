import Link from "next/link";

export default function Page() {
    return (
        <div>
            <div>
                <h1>
                    Listen <b>Together</b>
                </h1>
                <hr />
            </div>

            <div className="center-container">
                <Link href="/ythost">YTM Host</Link>
                <Link href="/ytclient">YTM Client</Link>
            </div>
        </div>
    )
}