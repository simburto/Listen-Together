import NextAuth from "next-auth"
import jwt from "next-auth/jwt"

import Spotify from "next-auth/providers/spotify"

import type { NextAuthConfig } from "next-auth"

export const config = {
  session: {
    strategy: "jwt",
  },
  theme: {
    logo: "https://next-auth.js.org/img/logo/logo-sm.png",
  },
  providers: [
    Spotify({
      authorization: "https://accounts.spotify.com/en/authorize?scope=app-remote-control+streaming+user-modify-playback-state+user-read-currently-playing+user-read-playback-state"
    }),
  ],
  callbacks: {
    async jwt({ token, account, user }) {
      if (account && user) {
        return {
          accessToken: account.access_token,
          refreshToken: account.refresh_token,
          user,
        }
      }
      return token
    },
    async session({ session, token }) {
      // @ts-ignore
      session.accessToken = token.accessToken
      return session
    },
    authorized({ request, auth }) {
      const { pathname } = request.nextUrl
      if (pathname === "/middleware-example") return !!auth
      return true
    },
  },
} satisfies NextAuthConfig

export const { handlers, auth, signIn, signOut } = NextAuth(config)
