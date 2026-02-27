"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  ReactNode,
} from "react";
import { User, UserHealthProfile } from "./types";

const AUTH_STORAGE_KEY = "nutricurator_auth";

export interface SignupHealthData {
  diabetes?: string;
  hypertension?: string;
  kidneydisease?: string;
  allergy?: string[];
}

interface AuthContextType {
  user: User | null;
  healthProfile: UserHealthProfile | null;
  isLoggedIn: boolean;
  token: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (
    email: string,
    password: string,
    healthData?: SignupHealthData,
  ) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function loadStoredAuth(): {
  user: User | null;
  healthProfile: UserHealthProfile | null;
  token: string | null;
} {
  if (typeof window === "undefined") return { user: null, healthProfile: null, token: null };
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return { user: null, healthProfile: null, token: null };
    const parsed = JSON.parse(raw) as {
      user: User;
      healthProfile: UserHealthProfile;
      token: string;
    };
    const token = parsed.token ?? null;
    // stale mock token/session cleanup
    if (!token || token.endsWith(".mock_signature")) {
      localStorage.removeItem(AUTH_STORAGE_KEY);
      return { user: null, healthProfile: null, token: null };
    }
    return { user: parsed.user ?? null, healthProfile: parsed.healthProfile ?? null, token };
  } catch {
    return { user: null, healthProfile: null, token: null };
  }
}

function saveAuth(user: User | null, healthProfile: UserHealthProfile | null, token: string | null = null) {
  if (typeof window === "undefined") return;
  try {
    if (!user || !token) {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    } else {
      localStorage.setItem(
        AUTH_STORAGE_KEY,
        JSON.stringify({ user, healthProfile, token }),
      );
    }
  } catch {}
}

function parseJwtSub(token: string): number | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = payload + "=".repeat((4 - (payload.length % 4)) % 4);
    const parsed = JSON.parse(atob(padded));
    const sub = Number(parsed?.sub);
    return Number.isFinite(sub) ? sub : null;
  } catch {
    return null;
  }
}

function toUser(userId: number, email: string): User {
  const now = new Date().toISOString();
  return {
    user_id: userId,
    email,
    created_at: now,
    updated_at: now,
    is_sensitive_agreed: false,
    agreed_at: now.slice(0, 19).replace("T", " "),
    is_tos_agreed: true,
    is_privacy_agreed: true,
  };
}

function toHealthProfile(raw: Record<string, unknown> | null, userId: number): UserHealthProfile | null {
  if (!raw) return null;
  return {
    user_id: userId,
    gender: String(raw.gender ?? ""),
    birth_date: String(raw.birth_date ?? ""),
    height: Number(raw.height ?? 0),
    weight: Number(raw.weight ?? 0),
    average_of_steps: Number(raw.average_of_steps ?? 0),
    activity_level: String(raw.activity_level ?? ""),
    diabetes: String(raw.diabetes ?? ""),
    hypertension: String(raw.hypertension ?? ""),
    kidneydisease: String(raw.kidneydisease ?? ""),
    allergy: Array.isArray(raw.allergy) ? raw.allergy.join(", ") : String(raw.allergy ?? ""),
    notes: String(raw.notes ?? ""),
    favorite: String(raw.favorite ?? ""),
    goal: String(raw.goal ?? ""),
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [healthProfile, setHealthProfile] =
    useState<UserHealthProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const { user: u, healthProfile: h, token: t } = loadStoredAuth();
    if (u && t) {
      setUser(u);
      setHealthProfile(h);
      setToken(t);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const loginRes = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: email, password }),
      });
      if (!loginRes.ok) return false;

      const loginData = await loginRes.json();
      const accessToken = loginData?.access_token;
      if (typeof accessToken !== "string" || !accessToken) return false;

      const userId = parseJwtSub(accessToken);
      if (!userId) return false;

      let profile: UserHealthProfile | null = null;
      try {
        const profileRes = await fetch("/api/v1/users/me/profile", {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (profileRes.ok) {
          const profileData = await profileRes.json();
          profile = toHealthProfile(profileData?.profile ?? null, userId);
        }
      } catch {}

      const nextUser = toUser(userId, email);
      setUser(nextUser);
      setHealthProfile(profile);
      setToken(accessToken);
      saveAuth(nextUser, profile, accessToken);
      return true;
    } catch {
      return false;
    }
  }, []);

  const signup = useCallback(
    async (
      email: string,
      password: string,
      healthData?: SignupHealthData,
    ) => {
      try {
        const signupRes = await fetch("/api/v1/auth/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: email,
            password,
            is_tos_agreed: true,
            is_privacy_agreed: true,
            is_sensitive_agreed:
              !!healthData?.allergy?.length ||
              !!healthData?.diabetes ||
              !!healthData?.hypertension ||
              !!healthData?.kidneydisease,
          }),
        });
        if (!signupRes.ok) return false;

        const signupData = await signupRes.json();
        const accessToken = signupData?.access_token;
        if (typeof accessToken !== "string" || !accessToken) return false;

        const userId = parseJwtSub(accessToken);
        if (!userId) return false;

        if (healthData && (healthData.diabetes || healthData.hypertension || healthData.kidneydisease || healthData.allergy?.length)) {
          await fetch("/api/v1/users/me/profile", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({
              diabetes: healthData.diabetes,
              hypertension: healthData.hypertension,
              kidneydisease: healthData.kidneydisease,
              allergy: healthData.allergy,
            }),
          });
        }

        let profile: UserHealthProfile | null = null;
        try {
          const profileRes = await fetch("/api/v1/users/me/profile", {
            headers: { Authorization: `Bearer ${accessToken}` },
          });
          if (profileRes.ok) {
            const profileData = await profileRes.json();
            profile = toHealthProfile(profileData?.profile ?? null, userId);
          }
        } catch {}

        const nextUser = toUser(userId, email);
        setUser(nextUser);
        setHealthProfile(profile);
        setToken(accessToken);
        saveAuth(nextUser, profile, accessToken);
        return true;
      } catch {
        return false;
      }
    },
    [],
  );

  const logout = useCallback(() => {
    if (token) {
      fetch("/api/v1/auth/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => undefined);
    }
    setUser(null);
    setHealthProfile(null);
    setToken(null);
    saveAuth(null, null, null);
  }, [token]);

  return (
    <AuthContext.Provider
      value={{
        user,
        healthProfile,
        isLoggedIn: !!user && !!token,
        token,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
