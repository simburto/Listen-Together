'use client';

import { useSession } from 'next-auth/react';

export default function DisplayToken() {
    const session = useSession();
    // @ts-ignore
    const refreshToken = session?.data?.refreshToken
  
    return (
        <div className="text-wrap">Refresh Token: {refreshToken}</div>
    );
}