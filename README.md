# Literature Review Archiver (Antigravity) 📚

이 프로젝트는 연구 논문(PDF)을 분석하여 Google Drive에 업로드하고, AI(Gemini)를 통해 요약 및 메타데이터를 추출하여 Notion 데이터베이스에 자동으로 정리해주는 도구입니다.

동료 연구자분들이 수집한 논문을 효율적으로 관리하고 공유할 수 있도록 돕기 위해 제작되었습니다.

## ✨ 주요 기능
1. **PDF 자동 감지**: `papers/` 폴더 내의 PDF 파일을 자동으로 찾습니다.
2. **Google Drive 연동**: 파일을 드라이브에 업로드하고 공유 링크를 생성합니다 (이미 있는 경우 링크 검색).
3. **AI 논문 분석**: Google Gemini 2.5 Pro 모델을 사용하여 논문의 핵심 내용, 연구 방법, 결과 등을 상세하게 한국어로 요약합니다.
4. **Notion 자동화**: 추출된 정보와 드라이브 링크를 Notion 데이터베이스에 자동으로 입력합니다.
5. **파일 정리**: 처리가 완료된 파일은 `papers/processed/` 폴더로 자동 이동됩니다.

## 🛠️ 사전 준비 (Prerequisites)

이 프로그램을 실행하기 위해서는 다음 3가지 키/설정이 필요합니다.

### 1. Notion API 설정
1. [Notion My Integrations](https://www.notion.so/my-integrations)에 접속하여 '새 통합(New Integration)'을 만듭니다.
2. '시크릿(Secret)' 키(`secret_...`로 시작)를 복사해둡니다.
3. 사용할 Notion 데이터베이스 페이지로 이동하여 `...` 메뉴 -> `연결(Connect)` -> 방금 만든 통합을 추가합니다.
4. 데이터베이스 URL에서 ID를 복사합니다.
   - 예: `https://www.notion.so/myworkspace/{database_id}?v=...` 에서 중괄호 부분에 해당하는 긴 문자열입니다.

### 2. Google Gemini API 키
1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받습니다.

### 3. Google Cloud Service Account (Google Drive용)
1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트를 만듭니다.
2. 'Google Drive API'를 검색하여 활성화(Enable)합니다.
3. '사용자 인증 정보(Credentials)' -> '서비스 계정 만들기(Create Service Account)'를 진행합니다.
4. 생성된 서비스 계정의 '키(Key)' 탭에서 '새 키 만들기' -> 'JSON'을 선택하여 다운로드합니다.
5. 다운로드한 파일을 프로젝트 폴더에 `service_account_key.json` 이름으로 저장합니다.
6. **중요**: 이 서비스 계정 이메일(`...@...iam.gserviceaccount.com`)을 복사하여, 검색하거나 업로드하려는 **Google Drive 폴더에 '편집자' 권한으로 공유**해주세요. (이 툴은 본인 드라이브 전체를 검색하는 것이 아니라, 서비스 계정이 접근 가능한 파일만 볼 수 있습니다. 다만 이 코드는 '전체 드라이브 검색' 로직을 일부 포함하므로, 서비스 계정이 파일에 접근 권한이 있어야 합니다.)

## 🚀 설치 및 실행 방법 (Installation & Usage)

### 1. 프로젝트 다운로드 및 설정
폴더를 다운로드 받은 후, 터미널(CMD 또는 PowerShell)을 열고 해당 폴더로 이동합니다.

```bash
# 필수 라이브러리 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (.env)
프로젝트 폴더의 `.env.example` 파일을 복사하여 `.env` 파일로 이름을 변경합니다.
그 후 `.env` 파일을 메모장으로 열어 위에서 준비한 키 값들을 입력합니다.

```ini
NOTION_KEY=secret_kjsdflk...
GEMINI_API_KEY=AIzaSy...
NOTION_DATABASE_ID=8d2j3...
GOOGLE_APPLICATION_CREDENTIALS=./service_account_key.json
```

### 3. 실행하기
1. 분석하고 싶은 PDF 파일들을 `papers/` 폴더 안에 넣습니다. (하위 폴더에 넣어도 됩니다.)
2. 프로그램을 실행합니다.

```bash
python main.py
```

3. 프로그램이 자동으로 PDF를 분석하고 Notion에 정리한 뒤, 완료된 파일은 `papers/processed/`로 옮깁니다.

## 📂 폴더 구조
```
.
├── main.py              # 메인 실행 파일
├── papers/              # [입력] 분석할 PDF 파일을 넣는 곳
│   └── processed/       # [완료] 처리가 끝난 파일이 이동되는 곳
├── utils/               # 유틸리티 스크립트 모음
├── requirements.txt     # 필요한 라이브러리 목록
├── .env                 # [중요] API 키 설정 파일 (공유 금지!)
└── service_account_key.json # [중요] 구글 인증 키 (공유 금지!)
```

## ⚠️ 주의사항
- `service_account_key.json` 파일과 `.env` 파일은 **절대로** 타인과 공유하거나 깃허브 등에 올리지 마세요. 개인 보안 정보가 포함되어 있습니다.

## 📊 Notion 데이터베이스 설정 (권장)
Notion 데이터베이스를 새로 만들 때, 아래 속성(Property)들을 미리 만들어두어야 코드가 정상 작동합니다.

| 속성 이름 | 속성 유형 (Type) |
| --- | --- |
| **논문 제목** | 제목 (Title) |
| **저자** | 텍스트 (Text) |
| **발행연도** | 숫자 (Number) |
| **학술지명/출처** | 텍스트 (Text) |
| **페이지** | 텍스트 (Text) |
| **핵심 키워드** | 다중 선택 (Multi-select) |
| **유형** | 선택 (Select) |
| **읽음 상태** | 상태 (Status) - 기본값: '읽을 예정' |
| **권(호)** | 텍스트 (Text) |
| **URL/DOI** | URL |
| **파일 첨부** | 파일과 미디어 (Files & Media) |

## 🧠 Gemini 시스템 프롬프트 (참고용)
AI가 논문을 분석할 때 사용하는 프롬프트입니다. `utils/gemini_utils.py` 파일에서 수정할 수 있습니다.

> **Role**: Expert Academic Researcher
> 
> **Analysis Points**:
> 1. **Metadata Extraction**: Title, Authors, Year, Journal, Page, Keywords, Type, DOI, etc.
> 2. **Detailed Summary**:
>    - 연구 목적 및 필요성
>    - 이론적 배경 (핵심 이론, 개념 정의)
>    - 연구 방법 (설계, 참여자, 데이터 수집)
>    - **연구 결과 (상세 분석 및 인용구 포함)**
>    - 논의 및 시사점
> 3. **Contextual Connection**: '마을교육공동체에 참여하는 중학교 교사들의 관계적 행위자성' 연구와의 연관성 분석

*자세한 프롬프트 내용은 소스 코드를 확인하세요.*
