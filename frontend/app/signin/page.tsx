'use client';

import { useSession } from 'next-auth/react';
import Login from '../shared/Login';
import Logout from '../signout/Logout';
import DisplayToken from './DisplayToken';

export default function SignOut() {
    const { data: session } = useSession();
    return session ? (
        <>
            <DisplayToken/>
            <Logout/>
        </>
    ) : (
        <div className='mt-8 mx-auto max-w-7xl sm:px-6 lg:px-8'>
            <Login />
        </div>
    );
}