import NextAuth from 'next-auth';
import SpotifyProvider from 'next-auth/providers/spotify';
import type { NextAuthOptions } from 'next-auth';

export const authOptions: NextAuthOptions = {
    secret: process.env.NEXTAUTH_SECRET,
    providers: [
        SpotifyProvider({
            clientId: process.env.SPOTIFY_CLIENT_ID!,
            clientSecret: process.env.SPOTIFY_CLIENT_SECRET!,
            authorization: "https://accounts.spotify.com/en/authorize?scope=app-remote-control+streaming+user-modify-playback-state+user-read-currently-playing+user-read-playback-state"
        })
    ],
    callbacks: {
        /*
        jwt: async ({user, token}) => {
            if (user) {
                // @ts-ignore
                token.accessToken = user.accessToken;
            }
            return token;
        },
        */
        jwt: async ({ token, account, user }) => {
            if (account && user) {
                token.accessToken = account.access_token;
                token.refreshToken = account.refresh_token;
            }
            return token
        },
        /*
        session: async ({session, token}) => {
            if (session?.user) {
                // @ts-ignore
                session.accessToken = token.accessToken;
                return session;
            }
            return session;
        }
        */
        session: async ({ session, token }) => {
            // @ts-ignore
            session.accessToken = token.accessToken
            // @ts-ignore
            session.refreshToken = token.refreshToken
            return session
        },
    },
    session: {
        strategy: 'jwt',
    },
}

export default NextAuth(authOptions);