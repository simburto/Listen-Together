import NextAuth from 'next-auth';
import SpotifyProvider from 'next-auth/providers/spotify';

const handler = NextAuth({
    providers: [
        SpotifyProvider({
            clientId: process.env.SPOTIFY_ID!,
            clientSecret: process.env.SPOTIFY_SECRET!,
        }),
    ]
})

export { handler as GET, handler as POST }