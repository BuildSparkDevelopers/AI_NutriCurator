"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useCart } from "@/lib/cart-context";
import {
  Search,
  MapPin,
  ShoppingCart,
  User,
  Menu,
  X,
  Heart,
  LogOut,
} from "lucide-react";

const navLinks = [
  { href: "/", label: "뉴큐추천" },
  { href: "/?cat=new", label: "신상품" },
  { href: "/?cat=best", label: "베스트" },
  { href: "/?cat=sale", label: "알뜰쇼핑" },
  { href: "/?cat=health", label: "건강식품" },
];

export default function Header() {
  const { isLoggedIn, user, logout } = useAuth();
  const { totalCount } = useCart();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-kurly-border">
      {/* Top utility bar */}
      <div className="bg-primary text-white text-xs">
        <div className="mx-auto max-w-[1050px] px-4 flex items-center justify-end gap-4 h-8">
          {isLoggedIn ? (
            <>
              <span className="hidden sm:inline">
                {user?.email}님 환영합니다
              </span>
              <button
                onClick={logout}
                className="hover:underline flex items-center gap-1"
              >
                <LogOut size={12} />
                로그아웃
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:underline">
                로그인
              </Link>
              <span className="text-white/40">|</span>
              <Link href="/signup" className="hover:underline">
                회원가입
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Main header */}
      <div className="mx-auto max-w-[1050px] px-4">
        <div className="flex items-center justify-between h-16">
          {/* Mobile menu toggle */}
          <button
            className="lg:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 shrink-0">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">N</span>
            </div>
            <h1 className="text-xl font-bold text-primary hidden sm:block">
              NutriCurator
            </h1>
          </Link>

          {/* Search bar */}
          <div className="hidden md:flex flex-1 max-w-[400px] mx-6">
            <div className="relative w-full">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="검색어를 입력해주세요"
                className="w-full h-10 pl-4 pr-10 border border-primary rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
              <button className="absolute right-3 top-1/2 -translate-y-1/2 text-primary">
                <Search size={20} />
              </button>
            </div>
          </div>

          {/* Icons */}
          <div className="flex items-center gap-3 sm:gap-5">
            <button className="hidden sm:flex flex-col items-center text-gray-500 hover:text-primary transition-colors">
              <MapPin size={22} />
              <span className="text-[10px] mt-0.5">배송지</span>
            </button>
            <button className="hidden sm:flex flex-col items-center text-gray-500 hover:text-primary transition-colors">
              <Heart size={22} />
              <span className="text-[10px] mt-0.5">찜한상품</span>
            </button>
            <Link
              href={isLoggedIn ? "/cart" : "/login"}
              className="relative flex flex-col items-center text-gray-500 hover:text-primary transition-colors"
            >
              <ShoppingCart size={22} />
              <span className="text-[10px] mt-0.5">장바구니</span>
              {totalCount > 0 && (
                <span className="absolute -top-1 -right-2 min-w-[16px] h-4 bg-primary text-white text-[10px] rounded-full flex items-center justify-center px-0.5">
                  {totalCount > 99 ? "99+" : totalCount}
                </span>
              )}
            </Link>
            <Link
              href={isLoggedIn ? "/" : "/login"}
              className="flex flex-col items-center text-gray-500 hover:text-primary transition-colors"
            >
              <User size={22} />
              <span className="text-[10px] mt-0.5">
                {isLoggedIn ? "마이페이지" : "로그인"}
              </span>
            </Link>
          </div>
        </div>
      </div>

      {/* Navigation bar */}
      <nav className="hidden lg:block border-t border-kurly-border">
        <div className="mx-auto max-w-[1050px] px-4">
          <ul className="flex items-center gap-8 h-12">
            {navLinks.map((link) => (
              <li key={link.label}>
                <Link
                  href={link.href}
                  className="text-sm font-medium text-gray-600 hover:text-primary transition-colors relative py-3"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-t border-kurly-border">
          <div className="px-4 py-3">
            <div className="relative mb-3">
              <input
                type="text"
                placeholder="검색어를 입력해주세요"
                className="w-full h-10 pl-4 pr-10 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
              <Search
                size={18}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
              />
            </div>
            <ul className="space-y-1">
              {navLinks.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="block py-2 text-sm text-gray-600 hover:text-primary"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </header>
  );
}
