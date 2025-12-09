# Signup Policy Flow (Terms & Privacy)

문서 위치: `/accounts/terms/`, `/accounts/privacy/`  
대상: 회원가입 시 이용약관/개인정보 처리방침 동의 UX 및 저장 흐름 정리

## 구성 요소
- Settings: `baseball/settings/base.py`
  - `TERMS_VERSION`, `PRIVACY_VERSION`
  - `TERMS_DOC_PATH`, `PRIVACY_DOC_PATH` (md 원본 경로)
  - `TERMS_URL`, `PRIVACY_URL`
- 모델: `accounts/models.py`
  - `terms_version`, `privacy_version`
  - `terms_agreed_at`, `privacy_agreed_at`
- 마이그레이션: `accounts/migrations/0002_user_policy_agreements.py`
- 폼: `accounts/forms.py`
  - `CustomUserCreationForm`에 `terms_agree`, `privacy_agree` BooleanField 추가
  - `save()`에서 버전/동의시각 저장
- 뷰: `accounts/views.py`
  - `terms()`, `privacy()` → `_render_policy`로 md 렌더
  - `auth_view()` 컨텍스트에 `terms_url`, `privacy_url` 전달
- 템플릿:
  - 가입 폼: `accounts/templates/auth.html`
    - 체크박스 + 정책 링크(현재 창에서 열림)
    - `sessionStorage` 플래그(`policy_agreed_terms/privacy`)를 읽어 체크 자동 반영 (`pageshow` 포함)
- 정책 페이지: `accounts/templates/policy.html`
  - 상/하단 “동의하고 돌아가기” 버튼 → `sessionStorage`에 플래그 set 후 `history.back()` (referrer 없으면 가입 페이지)

## 사용자 플로우
1) 가입 페이지(`/accounts/auth/?mode=signup`)에서 약관/개인정보 링크 클릭 → 같은 창에 정책 페이지 표시.  
2) 정책 페이지에서 “동의하고 돌아가기” 클릭 시:
   - `sessionStorage.policy_agreed_{terms|privacy} = true`
   - `history.back()` (referrer 없으면 `/accounts/auth/?mode=signup`로 이동)
3) 가입 페이지 로드시:
   - `sessionStorage` 플래그를 읽어 해당 체크박스 자동 체크 후 플래그 제거
4) 가입 폼 제출 시:
   - 체크박스 필수 검증
   - 저장 시 `terms_version`, `privacy_version`, `terms_agreed_at`, `privacy_agreed_at` 채움

## 기존 유저 재동의 플로우
- 미들웨어: `accounts.middleware.PolicyConsentRequiredMiddleware`
  - 로그인 사용자가 최신 버전(`TERMS_VERSION`/`PRIVACY_VERSION`)이 아니면 `/accounts/reconsent/`로 리디렉션 (`next` 포함)
  - 제외: terms/privacy/reconsent/auth/logout, static/media
- 재동의 뷰: `accounts.views.reconsent`
  - 폼: `ReconsentForm`(필수 체크 2개)
  - 성공 시 현재 버전과 동의시각 저장 후 `next`로 이동
- 템플릿: `accounts/templates/reconsent.html` (동의 체크 + 문서 보기 링크)

## 엔드포인트 요약
- 가입/로그인: `/accounts/auth/?mode=signup|login`
- 정책 보기: `/accounts/terms/`, `/accounts/privacy/`
- 재동의: `/accounts/reconsent/`

## 확인/운영 체크리스트
- 정책 md 경로: `docs/terms-of-service.md`, `docs/privacy-policy.md`
- 새 약관/정책 공개 시: 버전 상수 업데이트 → 필요 시 기존 유저 재동의 플로우 추가 검토
- 배포 전 마이그레이션: `python manage.py migrate` (0002 적용됨)
