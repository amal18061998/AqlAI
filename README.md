# AqlAI

**AI Chat Platform — Technical Reference**
*Multi-provider LLM router with Arabic language support*

---

## Project Overview

**AqlAI** (عقل — Arabic for "mind / intellect") is an AI-powered chat application built as a full-stack technical challenge. It enables users to:

- Converse with multiple LLM models in **English or Arabic**
- Manage full **chat history** across sessions
- Read an **AI-generated personal summary** of their interaction patterns
- **Export conversations** to PDF
- Switch languages dynamically with complete **RTL layout support for Arabic**

The project follows a clean separation between web-application concerns and AI inference logic, making the AI layer independently testable and provider-agnostic.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vue.js 3 (Composition API) |
| **State Management** | Pinia |
| **Styling** | Tailwind CSS (with RTL utilities) |
| **i18n** | vue-i18n — `en.json` / `ar.json` |
| **HTTP Client** | Axios (with JWT interceptor) |
| **Backend** | Django 4 + Django REST Framework |
| **Database** | SQLite3 |
| **Authentication** | JWT via `djangorestframework-simplejwt` |
| **LLM Provider 1** | Groq Cloud API |
| **LLM Provider 2** | Hugging Face Inference API |
| **LLM Provider 3** | DeepSeek API |
| **PDF Export** | jsPDF (client-side) |

---

## Architecture Philosophy

AqlAI separates its codebase into two conceptually distinct layers.

###  The Body — `apps/`

The Django apps (`authentication`, `chat`) handle all web application concerns:

- Who is this user? Are they authenticated?
- Save this message to the database
- Return this conversation history
- Apply rate limiting and validate input

These apps **do not know how AI works**. They only know that a service exists which takes text in and returns text out. They call `ai_services/router.py` and wait for a result.

### The Brain — `llm_services/`

This is a **pure Python module** — completely independent of Django, databases, and HTTP. It has one job:

> *"Given a list of messages and a model name, return the AI's response."*

It contains:
- An abstract `IProvider` base class that enforces a consistent interface across all vendors
- One concrete provider class per vendor (`groq_provider.py`, `huggingface_provider.py`)
- A `router.py` that selects the correct provider based on the model name sent by the frontend

This design means adding a new LLM provider (e.g., Anthropic, Cohere, Ollama) requires creating **one new file** and registering it in the router — no Django code is touched.

```
                 ┌─────────────────────────────┐
                 │       Django View            │
                 │  (apps/chat/views.py)        │
                 │                             │
                 │  1. Authenticate user        │
                 │  2. Save message to DB       │
                 │  3. Call ai_services router  │
                 │  4. Save response to DB      │
                 │  5. Return response          │
                 └──────────────┬──────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │    ai_services/router.py     │
                 │  model_name → provider?      │
                 └──┬──────────┬───────────────┘
                    │          │          │
            ┌───────┘   ┌──────┘   ┌──────┘
            ▼           ▼           ▼
       GroqProvider  Provider  HFProvider
```





---

## Architecture

All model selection is handled in `llm_services/router.py`. The user selects a model from the frontend dropdown; the router dispatches the request to the appropriate provider and model.

```
User → dropdown selection → llm_services/router.py → Provider API → Response
```

```
User selects model in dropdown
            │
            ▼
  llm_services/router.py
            │
  ┌─────────┴──────────────────────┐
  │                                │
  ▼                                ▼
Groq                          Hugging Face
  │                                │
  └─ llama-3.3-70b-versatile       ├─ google/gemma-3-27b-it
     (fast, default)               │  (structured tasks)
                                   └─ Qwen/Qwen2.5-72B-Instruct
                                      (long ctx, Arabic, reasoning)
```

---

## Provider 1 — Groq Cloud

**Model:** `llama-3.3-70b-versatile`

Groq's LPU (Language Processing Unit) hardware delivers significantly lower inference latency than GPU-based cloud providers, making it the default provider for real-time chat.

| Property | Value |
|---|---|
| Avg. throughput | ~800 tokens/sec (vs ~60 t/s on standard GPU clouds) |
| API format | OpenAI-compatible `/chat/completions` |
| Free tier | 14,400 req/day on most models |
| Arabic support | Yes — MSA confirmed |

### `llama-3.3-70b-versatile` — Default Conversational Model

Meta's LLaMA 3.3 70B is used as the **default model** for general conversations.

- **MMLU:** ~86% — competitive with frontier models at far lower inference cost
- **Arabic:** Broad multilingual corpus with strong MSA coverage; 70B scale significantly improves coherence over sub-10B models
- **Speed:** ~800 tokens/sec on Groq despite 70B parameter count, enabled by LPU architecture
- **Use case:** Fast general-purpose chat, the primary user-facing model

---

## Provider 2 — Hugging Face Inference API

**Models:** `google/gemma-3-27b-it` · `Qwen/Qwen2.5-72B-Instruct`

Hugging Face serves dual purposes: a **fallback inference provider** and a gateway to larger, specialized models not available on Groq. Vendor independence is achieved by routing via a single registry change in `router.py` — no other Django code is affected.

### `google/gemma-3-27b-it` — Structured Tasks & Instruction Following

Google DeepMind's Gemma 3 27B instruction-tuned model.

- **MMLU:** ~74%+ at the 27B tier — strong instruction adherence, purpose-built for chat and structured output
- **Use case:** Summaries, formatted answers, and translation requests where prompt-following precision matters more than raw knowledge
- **Multimodal-ready:** Supports vision inputs in capable deployments, leaving headroom for future expansion
  → [Gemma 2 technical report — Google DeepMind](https://storage.googleapis.com/deepmind-media/gemma/gemma2-report.pdf)

### `Qwen/Qwen2.5-72B-Instruct` — Long Context, Reasoning & Arabic

Alibaba's Qwen 2.5 72B instruction-tuned model.

- **MMLU:** ~85%+ — on par with top-tier open-weight models
- **Context window:** 128K tokens — suited for users pasting long code files or documents
- **Arabic:** Trained on a significantly larger multilingual corpus than prior generations, with notably improved coverage including MSA and dialectal variants
- **Use case:** Deep reasoning, long-document Q&A, and Arabic-heavy queries where language quality is paramount

---

## Model Selection Summary

| Model | Provider | Best For | Arabic |
|---|---|---|---|
| `llama-3.3-70b-versatile` | Groq | Fast general chat (default) | ✅ Strong |
| `google/gemma-3-27b-it` | Hugging Face | Structured tasks, formatting | ✅ Good |
| `Qwen/Qwen2.5-72B-Instruct` | Hugging Face | Long docs, reasoning, Arabic | ✅ Excellent |

> **Routing tip:** Qwen 2.5-72B is among the strongest open-weight models for Arabic NLP at this scale. For Arabic-heavy queries, routing to Qwen is recommended. For fast everyday chat, LLaMA 3.3-70B on Groq is the default.

---

## Adding or Swapping Models

All provider and model configuration lives in `llm_services/router.py`. To swap a model, update the `REGISTRY` constant — no other code changes are required.

To add an Arabic-specialized model from Hugging Face (e.g. CAMeL-Lab or AraGPT2):

1. Add the model ID to `REGISTRY` in `router.py`
2. Set the provider key to `huggingface`
3. Deploy — no Django views, serializers, or URL configuration changes needed

```python
Providers = {
    "llama-3.3-70b-versatile":    {"provider": "groq"},
    "google/gemma-3-27b-it":      {"provider": "huggingface"},
    "Qwen/Qwen2.5-72B-Instruct":  {"provider": "huggingface"},
    # Add new models here
}
```

---
### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env           # Fill in your API keys
python manage.py migrate
python manage.py createsuperuser  # Optional — access Django admin
```

### 3. Frontend setup

```bash
cd ../frontend
npm install
```

---

## Running the Application

### Quick start (recommended)

```bash
chmod +x run.sh
./run.sh
```

The `run.sh` script activates the Python virtual environment, starts the Django dev server, and launches the Vite dev server concurrently.

### Manual start

```bash
# Terminal 1 — Backend
cd backend && source venv/bin/activate && python manage.py runserver

# Terminal 2 — Frontend
cd frontend && npm run dev
```

| Service | URL |
|---|---|
| Frontend | `http://localhost:5173` |
| Backend API | `http://localhost:8000/api/` |
| Django Admin | `http://localhost:8000/admin/` |

---

### Authentication — `/api/auth/`

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/register/` | Create a new account | No |
| POST | `/api/auth/login/` | Obtain JWT access + refresh tokens | No |
| POST | `/api/auth/logout/` | Blacklist refresh token | Yes |
| GET | `/api/auth/me/` | Get authenticated user profile | Yes |
| PATCH | `/api/auth/me/` | Update language preference | Yes |
| POST | `/api/auth/token/refresh/` | Refresh access token | No |

### Chat — `/api/chat/`

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/chat/conversations/` | List all conversations | Yes |
| POST | `/api/chat/conversations/` | Start a new conversation | Yes |
| GET | `/api/chat/conversations/:id/` | Get all messages in a conversation | Yes |
| POST | `/api/chat/conversations/:id/message/` | Send a message → receive AI response | Yes |
| DELETE | `/api/chat/conversations/:id/` | Delete a conversation | Yes |
| GET | `/api/chat/models/` | List available AI models | Yes |

### Summary & Export — `/api/`

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/summary/` | Get AI-generated user summary | Yes |
| POST | `/api/summary/refresh/` | Re-generate summary from full history | Yes |
| GET | `/api/chat/conversations/:id/export/` | Export conversation as PDF | Yes |


## Internationalization (i18n)

### Setup

The frontend uses **vue-i18n v9** configured in `src/i18n/index.js`:

```js
import { createI18n } from 'vue-i18n'
import en from './en.json'
import ar from './ar.json'

export default createI18n({
  legacy: false,
  locale: localStorage.getItem('lang') || 'en',
  fallbackLocale: 'en',
  messages: { en, ar }
})
```

Language is persisted in the Pinia `i18n` store and synced to the user's backend profile, so the preference survives logout and multi-device sessions.

### Translation file structure

```json
// src/i18n/en.json
{
  "app": {
    "name": "AqlAI",
    "tagline": "Your Intelligent Conversation Partner"
  },
  "nav": {
    "home": "Home",
    "chat": "Chat",
    "profile": "Profile",
    "login": "Sign In",
    "signup": "Sign Up",
    "logout": "Sign Out"
  },
  "landing": {
    "hero_title": "AqlAI Smarter Conversations with Multiple AI Models",
    "hero_subtitle": "Switch seamlessly between top AI models in one unified interface. Ask anything in English or Arabic and receive intelligent, tailored responses. You can also download your conversations anytime.",
    "cta_start": "Start Chatting",
    "cta_learn": "Learn More", 
    "feature_PDF": "You can export your conversations as PDF file ",
    "feature_PDF_desc": " saving them in your device to read, share, or keep for later.",
    "feature_bilingual": "Bilingual Support",
    "feature_bilingual_desc": "Full English and Arabic support with proper RTL layout and localized responses.",
    "feature_history": "Smart History",
    "feature_history_desc": "Your conversations are saved and AI generates a summary of your interests over time.",
    "about_title": "Built for Thoughtful Conversations",
    "about_desc": "AqlAI combines multiple AI models into a single, beautiful interface. Whether you're researching, brainstorming, or just curious — switch models on the fly and get diverse perspectives."
  },
  "auth": {
    "login_title": "Welcome back",
    "login_subtitle": "Sign in to continue your conversations",
    "signup_title": "Create account",
    "signup_subtitle": "Join AqlAI and start exploring AI",
    "email": "Email",
    "username": "Username",
    "password": "Password",
    "confirm_password": "Confirm Password",
    "submit_login": "Sign In",
    "submit_signup": "Create Account",
    "no_account": "Don't have an account?",
    "has_account": "Already have an account?",
    "error_invalid": "Invalid credentials. Please try again.",
    "error_mismatch": "Passwords do not match.",
    "error_required": "This field is required.",
    "auth.error_email_format": "Please enter a valid email address"
  },
  "chat": {
    "new_chat": "New Chat",
    "send": "Send",
    "placeholder": "Type your message...",
    "select_model": "Select Model",
    "no_conversations": "No conversations yet",
    "start_prompt": "Start a conversation by typing a message below.",
    "thinking": "Thinking...",
    "error_send": "Failed to send message. Please try again.",
    "history": "Chat History",
    "delete_chat": "Delete",
    "model_groq": "Groq (LLaMA 3.3)",
    "model_hf_qwen": "HF Qwen 2.5",
    "model_hf_gemma": "HF Gemma 2",
    "search": "Search conversations...",
    "export_pdf": "Export as PDF"
  },
  "profile": {
    "title": "Your Profile",
    "summary_title": "AI-Generated Summary",
    "summary_empty": "Chat more to generate a summary of your interests and patterns.",
    "language_pref": "Language Preference",
    "total_chats": "Total Conversations",
    "total_messages": "Total Messages",
    "member_since": "Member Since",
    "refresh_summary": "Refresh",
    "summary_updated": "Summary updated!",
    "summary_not_enough": "Need at least 5 messages to generate a summary."
  },
  "common": {
    "loading": "Loading...",
    "error": "Something went wrong.",
    "retry": "Retry",
    "cancel": "Cancel",
    "save": "Save",
    "close": "Close"
  }
}

```

```json
// src/i18n/ar.json
{
  "app": {
    "name": "  عقلAI ",
    "tagline": "شريكك الذكي في المحادثات"
  },
  "nav": {
    "home": "الرئيسية",
    "chat": "المحادثة",
    "profile": "الملف الشخصي",
    "login": "تسجيل الدخول",
    "signup": "إنشاء حساب",
    "logout": "تسجيل الخروج"
  },
  "landing": {
    "hero_title": "AqlAI محادثات أكثر ذكاءً باستخدام نماذج ذكاء اصطناعي متعددة",
    "hero_subtitle": "يمكنك التبديل بسهولة بين أفضل نماذج الذكاء الاصطناعي ضمن واجهة موحدة. اطرح أي سؤال بالإنجليزية أو العربية واحصل على إجابات ذكية ومخصصة لاحتياجاتك. يمكنك أيضًا تنزيل محادثاتك في أي وقت.",
    "cta_start": "ابدأ المحادثة",
    "cta_learn": "اعرف المزيد",
    "feature_PDF": "تحميل المحادثات كملف PDF",
    "feature_PDF_desc": "يمكنك حفظها على جهازك لقراءتها أو مشاركتها أو الرجوع إليها لاحقاً",
    "feature_bilingual": "دعم ثنائي اللغة",
    "feature_bilingual_desc": "دعم كامل للعربية والإنجليزية مع تخطيط RTL صحيح وردود محلية.",
    "feature_history": "سجل ذكي",
    "feature_history_desc": "يتم حفظ محادثاتك ويقوم الذكاء الاصطناعي بإنشاء ملخص لاهتماماتك بمرور الوقت.",
    "about_title": "مصمم للمحادثات المدروسة",
    "about_desc": "يجمع بين نماذج ذكاء اصطناعي متعددة في واجهة واحدة جميلة. سواء كنت تبحث أو تفكر أو تستكشف — قم بتغيير النماذج بسرعة واحصل على وجهات نظر متنوعة."
  },
  "auth": {
    "login_title": "مرحبًا بعودتك",
    "login_subtitle": "سجّل الدخول لمتابعة محادثاتك",
    "signup_title": "إنشاء حساب",
    "signup_subtitle": "انضم وابدأ استكشاف الذكاء الاصطناعي",
    "email": "البريد الإلكتروني",
    "username": "اسم المستخدم",
    "password": "كلمة المرور",
    "confirm_password": "تأكيد كلمة المرور",
    "submit_login": "تسجيل الدخول",
    "submit_signup": "إنشاء الحساب",
    "no_account": "ليس لديك حساب؟",
    "has_account": "لديك حساب بالفعل؟",
    "error_invalid": "بيانات غير صحيحة. يرجى المحاولة مرة أخرى.",
    "error_mismatch": "كلمتا المرور غير متطابقتين.",
    "error_required": "هذا الحقل مطلوب.",
    "auth.error_email_format": "يرجى إدخال عنوان بريد إلكتروني صالح"
    
  },
  "chat": {
    "new_chat": "محادثة جديدة",
    "send": "إرسال",
    "placeholder": "اكتب رسالتك...",
    "select_model": "اختر النموذج",
    "no_conversations": "لا توجد محادثات بعد",
    "start_prompt": "ابدأ محادثة بكتابة رسالة أدناه.",
    "thinking": "جارٍ التفكير...",
    "error_send": "فشل إرسال الرسالة. يرجى المحاولة مرة أخرى.",
    "history": "سجل المحادثات",
    "delete_chat": "حذف",
    "model_groq": "Groq (LLaMA 3.3)",
    "model_hf_qwen": "HF Qwen 2.5",
    "model_hf_gemma": "HF Gemma 2",
    "search": "ابحث عن محادثة...",
    "export_pdf": "تصدير كملف PDF"
  },
  "profile": {
    "title": "ملفك الشخصي",
    "summary_title": "ملخص مُولَّد بالذكاء الاصطناعي",
    "summary_empty": "تحدث أكثر لإنشاء ملخص لاهتماماتك وأنماطك.",
    "language_pref": "تفضيل اللغة",
    "total_chats": "إجمالي المحادثات",
    "total_messages": "إجمالي الرسائل",
    "member_since": "عضو منذ",
    "refresh_summary": "تحديث",
    "summary_updated": "تم تحديث الملخص!",
    "summary_not_enough": "تحتاج 5 رسائل على الأقل لإنشاء ملخص."
  },
  "common": {
    "loading": "جارٍ التحميل...",
    "error": "حدث خطأ ما.",
    "retry": "إعادة المحاولة",
    "cancel": "إلغاء",
    "save": "حفظ",
    "close": "إغلاق"
  }
}
{
  "app": {
    "name": "  عقلAI ",
    "tagline": "شريكك الذكي في المحادثات"
  },
  "nav": {
    "home": "الرئيسية",
    "chat": "المحادثة",
    "profile": "الملف الشخصي",
    "login": "تسجيل الدخول",
    "signup": "إنشاء حساب",
    "logout": "تسجيل الخروج"
  },
  "landing": {
    "hero_title": "AqlAI محادثات أكثر ذكاءً باستخدام نماذج ذكاء اصطناعي متعددة",
    "hero_subtitle": "يمكنك التبديل بسهولة بين أفضل نماذج الذكاء الاصطناعي ضمن واجهة موحدة. اطرح أي سؤال بالإنجليزية أو العربية واحصل على إجابات ذكية ومخصصة لاحتياجاتك. يمكنك أيضًا تنزيل محادثاتك في أي وقت.",
    "cta_start": "ابدأ المحادثة",
    "cta_learn": "اعرف المزيد",
    "feature_PDF": "تحميل المحادثات كملف PDF",
    "feature_PDF_desc": "يمكنك حفظها على جهازك لقراءتها أو مشاركتها أو الرجوع إليها لاحقاً",
    "feature_bilingual": "دعم ثنائي اللغة",
    "feature_bilingual_desc": "دعم كامل للعربية والإنجليزية مع تخطيط RTL صحيح وردود محلية.",
    "feature_history": "سجل ذكي",
    "feature_history_desc": "يتم حفظ محادثاتك ويقوم الذكاء الاصطناعي بإنشاء ملخص لاهتماماتك بمرور الوقت.",
    "about_title": "مصمم للمحادثات المدروسة",
    "about_desc": "يجمع بين نماذج ذكاء اصطناعي متعددة في واجهة واحدة جميلة. سواء كنت تبحث أو تفكر أو تستكشف — قم بتغيير النماذج بسرعة واحصل على وجهات نظر متنوعة."
  },
  "auth": {
    "login_title": "مرحبًا بعودتك",
    "login_subtitle": "سجّل الدخول لمتابعة محادثاتك",
    "signup_title": "إنشاء حساب",
    "signup_subtitle": "انضم وابدأ استكشاف الذكاء الاصطناعي",
    "email": "البريد الإلكتروني",
    "username": "اسم المستخدم",
    "password": "كلمة المرور",
    "confirm_password": "تأكيد كلمة المرور",
    "submit_login": "تسجيل الدخول",
    "submit_signup": "إنشاء الحساب",
    "no_account": "ليس لديك حساب؟",
    "has_account": "لديك حساب بالفعل؟",
    "error_invalid": "بيانات غير صحيحة. يرجى المحاولة مرة أخرى.",
    "error_mismatch": "كلمتا المرور غير متطابقتين.",
    "error_required": "هذا الحقل مطلوب.",
    "auth.error_email_format": "يرجى إدخال عنوان بريد إلكتروني صالح"
    
  },
  "chat": {
    "new_chat": "محادثة جديدة",
    "send": "إرسال",
    "placeholder": "اكتب رسالتك...",
    "select_model": "اختر النموذج",
    "no_conversations": "لا توجد محادثات بعد",
    "start_prompt": "ابدأ محادثة بكتابة رسالة أدناه.",
    "thinking": "جارٍ التفكير...",
    "error_send": "فشل إرسال الرسالة. يرجى المحاولة مرة أخرى.",
    "history": "سجل المحادثات",
    "delete_chat": "حذف",
    "model_groq": "Groq (LLaMA 3.3)",
    "model_hf_qwen": "HF Qwen 2.5",
    "model_hf_gemma": "HF Gemma 2",
    "search": "ابحث عن محادثة...",
    "export_pdf": "تصدير كملف PDF"
  },
  "profile": {
    "title": "ملفك الشخصي",
    "summary_title": "ملخص مُولَّد بالذكاء الاصطناعي",
    "summary_empty": "تحدث أكثر لإنشاء ملخص لاهتماماتك وأنماطك.",
    "language_pref": "تفضيل اللغة",
    "total_chats": "إجمالي المحادثات",
    "total_messages": "إجمالي الرسائل",
    "member_since": "عضو منذ",
    "refresh_summary": "تحديث",
    "summary_updated": "تم تحديث الملخص!",
    "summary_not_enough": "تحتاج 5 رسائل على الأقل لإنشاء ملخص."
  },
  "common": {
    "loading": "جارٍ التحميل...",
    "error": "حدث خطأ ما.",
    "retry": "إعادة المحاولة",
    "cancel": "إلغاء",
    "save": "حفظ",
    "close": "إغلاق"
  }
}

```

### RTL Support

Arabic layout is driven by five layers:

1. `dir="rtl"` set on `<html>` dynamically when locale switches to `ar`
2. Tailwind CSS `rtl:` variants for mirrored layouts (`rtl:flex-row-reverse`, `rtl:text-right`, `rtl:mr-0 rtl:ml-4`)
3. `src/assets/styles/rtl.css` for overrides Tailwind cannot handle declaratively (e.g., chat bubble tails, sidebar slide direction)
4. **Noto Sans Arabic** font via Google Fonts — ensures proper glyph shaping and Arabic ligature rendering
5. AI system prompt is prepended with a language instruction at the `ai_services` layer:

## Export & Summary Features

### PDF Export

Conversations are exported client-side using **jsPDF**. Each PDF includes:
- Conversation title and export date
- All messages with `You` / `AqlAI` labels
- The model name used in the session
- Correct text direction (`rtl`) for Arabic exports

### AI-Generated User Summary

`llm_services/summary.py` calls the AI with a structured prompt after a session threshold is met:

```
System: You are an assistant that summarizes user behavior.
        Respond in {language}. Be concise — 3 to 5 sentences.

User: Based on the following chat history, summarize:
      - This user's main interests and recurring topics
      - Their query style (detailed vs. brief, technical vs. casual)
      - Any notable patterns

      Chat history:
      {last_50_messages}
```

The summary is stored on the `CustomUser` model and displayed on the profile page. It refreshes either manually (via "Refresh Summary" button) or automatically when the user accumulates 20 new messages since the last refresh.

---

## AI-Assisted Development

This project was developed with the assistance of **Claude (Anthropic)** and **CHATGPT**and**GLM5**.

**How they were used:**
- Generating DRF serializer and view boilerplate
- Suggesting the `AIProvider` abstract base class pattern for the `llm_services` module
- Autocompleting vue-i18n setup and Pinia store structures
- Debugging CORS configuration and JWT cookie handling edge cases
- Drafting initial unit test scaffolding for the router


---

## References

- [Meta LLaMA 3 release blog](https://ai.meta.com/blog/meta-llama-3/)
- [Gemma 2 technical report — Google DeepMind](https://storage.googleapis.com/deepmind-media/gemma/gemma2-report.pdf)
- [Mistral 7B paper — arXiv:2310.06825](https://arxiv.org/abs/2310.06825)
- [ArabicMMLU dataset & leaderboard — MBZUAI](https://huggingface.co/datasets/MBZUAI/ArabicMMLU)
- [CAMeL-Lab Arabic NLP models](https://huggingface.co/CAMeL-Lab)
- [Open LLM Leaderboard — Hugging Face](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)
