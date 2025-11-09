# Troubleshooting Guide

## 레이아웃 CSS 문제 해결

### 문제 발생
- **증상**: Frontend UI가 레이아웃 없이 텍스트만 세로로 나열되는 현상
- **원인**: Vite 기본 CSS와 Tailwind CSS 설정 불일치
- **영향 범위**: 전체 UI 구조 (헤더, 사이드바, 메인 콘텐츠)

### 근본 원인 분석

#### 1. **src/index.css의 Vite 보일러플레이트 CSS**
```css
/* 문제: body가 flex centering으로 설정됨 */
body {
  display: flex;
  place-items: center;  /* 모든 내용을 중앙에 배치 */
  min-height: 100vh;
}
```
→ Tailwind의 flex 레이아웃을 모두 무시하고 강제로 중앙정렬

#### 2. **Tailwind v4 vs v3 호환성**
- 설치되어 있던 패키지: `tailwindcss@4.1.17` + `@tailwindcss/postcss@4.1.17`
- PostCSS 설정: `@tailwindcss/postcss` 플러그인 사용
- 문제: `@tailwind` 지시문이 제대로 컴파일되지 않음

#### 3. **PostCSS 설정 오류**
```js
/* 잘못된 설정 */
plugins: {
  '@tailwindcss/postcss': {},
}
```
→ Tailwind v3과 v4에서 다른 설정 필요

### 해결 방법

#### Step 1: index.css 수정
```css
/* 기존 */
body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

/* 변경 후 */
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #root {
  height: 100%;
  width: 100%;
}
```

#### Step 2: Tailwind v4 → v3으로 다운그레이드
```bash
npm install tailwindcss@3 --save-dev
```

**이유**:
- Tailwind v4는 새로운 PostCSS 플러그인 시스템 사용
- 기존 프로젝트와 호환성 문제
- v3가 더 안정적이고 검증된 버전

#### Step 3: PostCSS 설정 수정
```js
/* 변경 후 */
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

#### Step 4: tailwind.config.ts 단순화
```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

export default config
```

#### Step 5: App.css 정리
```css
/* 변경 후 */
/* App Component Styles */
/* All styling is handled by Tailwind CSS */
```

#### Step 6: 미사용 imports 제거
```ts
/* src/services/websocket.ts */
// 제거: import { apiClient } from './api';
```

### 검증

✅ 모든 변경 후:
1. `npm run dev` 실행
2. `http://localhost:3200` 접속
3. 레이아웃이 제대로 표시되는지 확인
4. 다크 모드 전환 정상 작동
5. 반응형 디자인(모바일) 정상 작동

### 예방책

1. **Vite 보일러플레이트 제거**
   - 새 프로젝트에서 불필요한 CSS 즉시 제거
   - Tailwind만 사용하도록 통일

2. **Tailwind 버전 관리**
   - package.json에서 버전 고정 권장
   - v3 사용 시: `"tailwindcss": "^3.4.0"`

3. **CSS 우선순위 명확히**
   - 전역 CSS는 최소한으로 유지
   - 컴포넌트 스타일은 Tailwind class로만 정의

### 관련 파일

| 파일 | 변경사항 |
|------|---------|
| `motorbot-frontend/src/index.css` | Vite CSS 제거, Tailwind 지시문 추가 |
| `motorbot-frontend/src/App.css` | 보일러플레이트 CSS 제거 |
| `motorbot-frontend/postcss.config.js` | v3 설정으로 수정 |
| `motorbot-frontend/tailwind.config.ts` | 설정 단순화 |
| `motorbot-frontend/src/services/websocket.ts` | 미사용 import 제거 |

---

## 기타 주의사항

### 개발 환경 설정
- Node.js: v18+ 권장
- npm: v8+ 권장
- 포트: 3200 (frontend), 3201 (backend)

### 빌드 및 배포
```bash
# 프로덕션 빌드
npm run build

# 타입 체크
tsc -b

# 린트 확인
npm run lint
```

### 트러블슈팅 팁
- CSS 변경 후 브라우저 캐시 삭제 필수 (Cmd+Shift+Delete)
- 개발 서버 재시작: Ctrl+C → `npm run dev`
- node_modules 문제 시: `rm -rf node_modules && npm install`
