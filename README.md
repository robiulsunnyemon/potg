# POTG Authentication Module (FastAPI)

এটি POTG প্রজেক্টের Authentication Module, যা FastAPI, Prisma, PostgreSQL এবং JWT Security দিয়ে তৈরি করা হয়েছে।

## 🚀 Features
- 🔐 JWT Authentication (Access & Refresh Tokens)
- 📧 Email OTP Verification (Registration & Password Reset)
- 👥 Role-based Access Control (Admin / User)
- 🛡️ Password Hashing (bcrypt)
- 📦 Prisma ORM Integration
- 🧩 Custom Exceptions & Response Mapping

## 🛠️ Tech Stack
- FastAPI
- Prisma Client Python
- PostgreSQL
- Poetry (Dependency Management)
- aiosmtplib (Async Email)
- Python-JOSE (JWT Management)

## 📦 Setup & Run

### 1️⃣ Install Dependencies
```bash
poetry install
```

### 2️⃣ Environment Variables
`.env` ফাইল কপি করে `.env` তৈরি করুন এবং আপনার ডেটাবেইজ ও ইমেইল ক্রেডেনশিয়াল দিন।
```bash
cp .env
```

### 3️⃣ Database Migration
PostgreSQL এ ডাটাবেজ (`potg_db`) তৈরি করুন এবং মাইগ্রেশন রান করুন:
```bash
poetry run prisma db push
## OR
poetry run prisma migrate dev
```

### 4️⃣ Run the Server
```bash
poetry run uvicorn app.main:app --reload
```

## 📝 API Endpoints

| Endpoint                                | Method | Description                                |
|-----------------------------------------|--------|--------------------------------------------|
| `/auth/signup`                          | POST   | নতুন একাউন্ট ক্রিয়েট ও OTP সেন্ড             |
| `/auth/login`                           | POST   | লগইন, JWT Access & Refresh Token রিটার্ন   |
| `/auth/resend-otp`                      | POST   | পুনরায় OTP সেন্ড                          |
| `/auth/otp-verification`                | POST   | একাউন্ট ভেরিফাই ও একটিভ করা                |
| `/auth/forget-password`                 | POST   | মেইলে পাসওয়ার্ড রিসেট OTP সেন্ড             |
| `/auth/forget-password-otp-verification`| POST   | OTP ভেরিফাই করে Reset Token রিটার্ন        |
| `/auth/reset-password`                  | POST   | Reset Token ও নতুন পাসওয়ার্ড দিয়ে রিসেট |
| `/auth/user-action`                     | PATCH  | ইউজারের স্ট্যাটাস পরিবর্তন (Admin Only)    |

## 🔑 Email Validation Note
পাসওয়ার্ডে অন্তত একটি বড় হাতের অক্ষর, ছোট হাতের অক্ষর, সংখ্যা এবং স্পেশাল ক্যারেক্টার থাকতে হবে। ফোন নম্বর ও ইমেইল যথাযথভাবে ভ্যালিডেট করা হয়েছে।
