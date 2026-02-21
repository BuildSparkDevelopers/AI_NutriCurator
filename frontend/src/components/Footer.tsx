import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-white border-t border-kurly-border mt-16">
      <div className="mx-auto max-w-[1050px] px-4 py-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
          <div>
            <h4 className="text-sm font-bold text-gray-600 mb-4">
              고객행복센터
            </h4>
            <p className="text-2xl font-bold text-gray-600 mb-2">
              1644-0000
            </p>
            <p className="text-xs text-gray-400 leading-relaxed">
              월~토요일 오전 7시 - 오후 6시
            </p>
          </div>
          <div>
            <h4 className="text-sm font-bold text-gray-600 mb-4">
              회사소개
            </h4>
            <ul className="space-y-2">
              {["NutriCurator 소개", "인재채용", "이용약관", "개인정보처리방침"].map(
                (item) => (
                  <li key={item}>
                    <Link
                      href="/"
                      className="text-xs text-gray-400 hover:text-primary transition-colors"
                    >
                      {item}
                    </Link>
                  </li>
                ),
              )}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-bold text-gray-600 mb-4">
              고객센터
            </h4>
            <ul className="space-y-2">
              {["공지사항", "자주하는 질문", "1:1 문의", "대량주문 문의"].map(
                (item) => (
                  <li key={item}>
                    <Link
                      href="/"
                      className="text-xs text-gray-400 hover:text-primary transition-colors"
                    >
                      {item}
                    </Link>
                  </li>
                ),
              )}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-bold text-gray-600 mb-4">
              AI 건강 분석
            </h4>
            <p className="text-xs text-gray-400 leading-relaxed">
              NutriCurator는 AI 기반 건강 분석으로
              <br />
              사용자에게 맞춤형 식품을 추천합니다.
            </p>
          </div>
        </div>

        <div className="border-t border-kurly-border pt-6">
          <p className="text-xs text-gray-400 leading-relaxed">
            법인명 (상호) : 주식회사 뉴트리큐레이터 | 사업자등록번호 :
            000-00-00000
            <br />
            통신판매업 : 제 2026-서울강남-00000 호 | 개인정보보호책임자 :
            홍길동
            <br />
            주소 : 서울특별시 강남구 테헤란로 000, 0층 (역삼동)
          </p>
          <p className="text-xs text-gray-300 mt-4">
            © AI-NutriCurator. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
