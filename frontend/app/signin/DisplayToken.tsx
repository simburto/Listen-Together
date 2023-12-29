'use client';

import { useSession } from 'next-auth/react';

export default function DisplayToken() {
    const session = useSession();
    // @ts-ignore
    const accessToken = session?.data?.accessToken
  
    return (
        <div>{accessToken}</div>
    );
}