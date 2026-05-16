"use client";

import { setAuthToken } from "@/lib/api";

const TOKEN_KEY = "pg_token";

export function saveToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
  setAuthToken(token);
}

export function loadToken() {
  const token = typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
  if (token) setAuthToken(token);
  return token;
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  setAuthToken(undefined);
}
