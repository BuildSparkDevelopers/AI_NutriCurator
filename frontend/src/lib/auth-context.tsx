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

const mockUser: User = {
  user_id: 101,
  email: "user101@example.com",
  created_at: "2026-02-20T10:15:30+09:00",
  updated_at: "2026-02-20T10:15:30+09:00",
  is_sensitive_agreed: true,
  agreed_at: "2026-02-20 10:14:55",
  is_tos_agreed: true,
  is_privacy_agreed: true,
};

const mockHealthProfile: UserHealthProfile = {
  user_id: 101,
  gender: "F",
  birth_date: "1995-07-12 00:00:00",
  height: 165.3,
  weight: 58.75,
  average_of_steps: 8421,
  activity_level: "3~4회",
  diabetes: "N/A",
  hypertension: "prehypertension",
  kidneydisease: "N/A",
  allergy: "Peanut",
  notes: "가벼운 운동 권장, 저염식 선호",
  favorite: "매운 음식",
  goal: "다이어트",
};

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
    return {
      user: parsed.user ?? null,
      healthProfile: parsed.healthProfile ?? null,
      token: parsed.token ?? null,
    };
  } catch {
    return { user: null, healthProfile: null, token: null };
  }
}

function saveAuth(user: User | null, healthProfile: UserHealthProfile | null, token: string | null = null) {
  if (typeof window === "undefined") return;
  try {
    if (!user || !healthProfile) {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    } else {
      localStorage.setItem(
        AUTH_STORAGE_KEY,
        JSON.stringify({ user, healthProfile, token }),
      );
    }
  } catch {}
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [healthProfile, setHealthProfile] =
    useState<UserHealthProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const { user: u, healthProfile: h, token: t } = loadStoredAuth();
    if (u && h) {
      setUser(u);
      setHealthProfile(h);
      setToken(t);
    }
  }, []);

  const generateMockToken = (userId: number): string => {
    // Mock JWT 토큰 생성 (실제로는 백엔드에서 제공해야 함)
    const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
    const payload = btoa(JSON.stringify({ sub: userId, iat: Date.now() }));
    const signature = "mock_signature";
    return `${header}.${payload}.${signature}`;
  };

  const login = useCallback(async (email: string, _password: string) => {
    if (email) {
      const newUser = { ...mockUser, email };
      const newToken = generateMockToken(newUser.user_id);
      setUser(newUser);
      setHealthProfile(mockHealthProfile);
      setToken(newToken);
      saveAuth(newUser, mockHealthProfile, newToken);
      return true;
    }
    return false;
  }, []);

  const signup = useCallback(
    async (
      email: string,
      _password: string,
      healthData?: SignupHealthData,
    ) => {
      if (!email) return false;
      const now = new Date().toISOString();
      const newUser = {
        user_id: 102,
        email,
        created_at: now,
        updated_at: now,
        is_sensitive_agreed:
          !!healthData?.allergy?.length ||
          !!healthData?.diabetes ||
          !!healthData?.hypertension ||
          !!healthData?.kidneydisease,
        agreed_at: now.slice(0, 19).replace("T", " "),
        is_tos_agreed: true,
        is_privacy_agreed: true,
      };
      const newProfile = {
        user_id: 102,
        gender: "",
        birth_date: "",
        height: 0,
        weight: 0,
        average_of_steps: 0,
        activity_level: "",
        diabetes: healthData?.diabetes || "N/A",
        hypertension: healthData?.hypertension || "N/A",
        kidneydisease: healthData?.kidneydisease || "N/A",
        allergy: healthData?.allergy?.join(", ") || "",
        notes: "",
        favorite: "",
        goal: "",
      };
      const newToken = generateMockToken(newUser.user_id);
      setUser(newUser);
      setHealthProfile(newProfile);
      setToken(newToken);
      saveAuth(newUser, newProfile, newToken);
      return true;
    },
    [],
  );

  const logout = useCallback(() => {
    setUser(null);
    setHealthProfile(null);
    setToken(null);
    saveAuth(null, null, null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        healthProfile,
        isLoggedIn: !!user,
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
