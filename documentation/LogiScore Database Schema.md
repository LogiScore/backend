| markdown_export|
|  |
| # LogiScore Database Schema Export

Generated on: 2025-08-14 01:51:16.80389+00

## Tables Overview

| Table | Columns | Live Rows | Relationships |
|-------|---------|-----------|--------------|
| `branches` | 11 | 0 | Yes |

## Detailed Schema

### `branches`

**Columns:** 11

| Column | Type |
|--------|------|
| id | uuid NOT NULL DEFAULT uuid_generate_v4() |
| freight_forwarder_id | uuid |
| name | character varying(255) NOT NULL |
| country | character varying(100) |
| city | character varying(100) |
| address | text |
| contact_email | character varying(255) |
| contact_phone | character varying(50) |
| is_active | boolean DEFAULT true |
| created_at | timestamp with time zone DEFAULT now() |
| updated_at | timestamp with time zone DEFAULT now() |

**Foreign Keys:**
- `branches.freight_forwarder_id` → `freight_forwarders.id`

**Indexes:**
- `branches_pkey` (CREATE UNIQUE INDEX branches_pkey ON public.branches USING btree (id))
- `idx_branches_freight_forwarder_id` (CREATE INDEX idx_branches_freight_forwarder_id ON public.branches USING btree (freight_forwarder_id))

---

## Relationships Summary

### High Level Relationships
- **users** 1 ⟶ ∞ **user_sessions**
- **freight_forwarders** 1 ⟶ ∞ **branches**
- **users** 1 ⟶ ∞ **reviews**
- **branches** 1 ⟶ ∞ **reviews**
- **freight_forwarders** 1 ⟶ ∞ **reviews**
- **reviews** 1 ⟶ ∞ **review_category_scores**
- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)
- **users** 1 ⟶ ∞ **disputes**
- **reviews** 1 ⟶ ∞ **disputes**
- **freight_forwarders** 1 ⟶ ∞ **disputes**
- **users** 1 ⟶ ∞ **disputes (resolved_by)**
- **freight_forwarders** 1 ⟶ ∞ **campaigns**

### Key Notes
- A review belongs to both a **branch** and the parent **freight_forwarder**
- **review_category_scores** stores individual question ratings (35 questions per review)
- **review_questions** serves as a reference table for current question set and rating criteria
- Disputes can be filed by a user and optionally resolved by another user
- The structure supports detailed analytics on individual question performance

## Export Information
- **Total Tables:** 1
- **Total Columns:** 11
- **Total Live Rows:** 0
- **Export Date:** 2025-08-14 01:51:16.80389+00
- **Database:** LogiScore Backend v0|
| # LogiScore Database Schema Export

Generated on: 2025-08-14 01:51:16.80389+00

## Tables Overview

| Table | Columns | Live Rows | Relationships |
|-------|---------|-----------|--------------|
| `disputes` | 12 | 0 | Yes |

## Detailed Schema

### `disputes`

**Columns:** 12

| Column | Type |
|--------|------|
| id | uuid NOT NULL DEFAULT uuid_generate_v4() |
| review_id | uuid |
| user_id | uuid |
| freight_forwarder_id | uuid |
| dispute_type | character varying(50) |
| description | text NOT NULL |
| status | character varying(20) DEFAULT 'pending'::character varying |
| admin_notes | text |
| resolved_by | uuid |
| resolved_at | timestamp with time zone |
| created_at | timestamp with time zone DEFAULT now() |
| updated_at | timestamp with time zone DEFAULT now() |

**Foreign Keys:**
- `disputes.freight_forwarder_id` → `freight_forwarders.id`
- `disputes.resolved_by` → `users.id`
- `disputes.review_id` → `reviews.id`
- `disputes.user_id` → `users.id`

**Indexes:**
- `disputes_pkey` (CREATE UNIQUE INDEX disputes_pkey ON public.disputes USING btree (id))
- `idx_disputes_review_id` (CREATE INDEX idx_disputes_review_id ON public.disputes USING btree (review_id))
- `idx_disputes_status` (CREATE INDEX idx_disputes_status ON public.disputes USING btree (status))

---

## Relationships Summary

### High Level Relationships
- **users** 1 ⟶ ∞ **user_sessions**
- **freight_forwarders** 1 ⟶ ∞ **branches**
- **users** 1 ⟶ ∞ **reviews**
- **branches** 1 ⟶ ∞ **reviews**
- **freight_forwarders** 1 ⟶ ∞ **reviews**
- **reviews** 1 ⟶ ∞ **review_category_scores**
- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)
- **users** 1 ⟶ ∞ **disputes**
- **reviews** 1 ⟶ ∞ **disputes**
- **freight_forwarders** 1 ⟶ ∞ **disputes**
- **users** 1 ⟶ ∞ **disputes (resolved_by)**
- **freight_forwarders** 1 ⟶ ∞ **campaigns**

### Key Notes
- A review belongs to both a **branch** and the parent **freight_forwarder**
- **review_category_scores** stores individual question ratings (35 questions per review)
- **review_questions** serves as a reference table for current question set and rating criteria
- Disputes can be filed by a user and optionally resolved by another user
- The structure supports detailed analytics on individual question performance

## Export Information
- **Total Tables:** 1
- **Total Columns:** 12
- **Total Live Rows:** 0
- **Export Date:** 2025-08-14 01:51:16.80389+00
- **Database:** LogiScore Backend v0|
| # LogiScore Database Schema Export

Generated on: 2025-08-14 01:51:16.80389+00

## Tables Overview

| Table | Columns | Live Rows | Relationships |
|-------|---------|-----------|--------------|
| `freight_forwarders` | 10 | 13 | No |

## Detailed Schema

### `freight_forwarders`

**Columns:** 10

| Column | Type |
|--------|------|
| id | uuid NOT NULL DEFAULT uuid_generate_v4() |
| name | character varying(255) NOT NULL |
| website | character varying(500) |
| logo_url | text |
| created_at | timestamp with time zone DEFAULT now() |
| description | text |
| headquarters_country | character varying(255) |
| global_rank | integer(32,0) |
| is_active | boolean DEFAULT true |
| updated_at | timestamp with time zone DEFAULT now() |

**Indexes:**
- `freight_forwarders_pkey` (CREATE UNIQUE INDEX freight_forwarders_pkey ON public.freight_forwarders USING btree (id))

**Statistics:** 13 live rows, 14 total inserts

---

## Relationships Summary

### High Level Relationships
- **users** 1 ⟶ ∞ **user_sessions**
- **freight_forwarders** 1 ⟶ ∞ **branches**
- **users** 1 ⟶ ∞ **reviews**
- **branches** 1 ⟶ ∞ **reviews**
- **freight_forwarders** 1 ⟶ ∞ **reviews**
- **reviews** 1 ⟶ ∞ **review_category_scores**
- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)
- **users** 1 ⟶ ∞ **disputes**
- **reviews** 1 ⟶ ∞ **disputes**
- **freight_forwarders** 1 ⟶ ∞ **disputes**
- **users** 1 ⟶ ∞ **disputes (resolved_by)**
- **freight_forwarders** 1 ⟶ ∞ **campaigns**

### Key Notes
- A review belongs to both a **branch** and the parent **freight_forwarder**
- **review_category_scores** stores individual question ratings (35 questions per review)
- **review_questions** serves as a reference table for current question set and rating criteria
- Disputes can be filed by a user and optionally resolved by another user
- The structure supports detailed analytics on individual question performance

## Export Information
- **Total Tables:** 1
- **Total Columns:** 10
- **Total Live Rows:** 13
- **Export Date:** 2025-08-14 01:51:16.80389+00
- **Database:** LogiScore Backend v0|
| # LogiScore Database Schema Export

Generated on: 2025-08-14 01:51:16.80389+00

## Tables Overview

| Table | Columns | Live Rows | Relationships |
|-------|---------|-----------|--------------|
| `review_category_scores` | 10 | 0 | Yes |

## Detailed Schema

### `review_category_scores`

**Columns:** 10

| Column | Type |
|--------|------|
| id | uuid NOT NULL DEFAULT gen_random_uuid() |
| review_id | uuid NOT NULL |
| category_id | character varying NOT NULL |
| category_name | character varying NOT NULL |
| question_id | character varying NOT NULL |
| question_text | text NOT NULL |
| rating | integer(32,0) NOT NULL |
| rating_definition | text |
| weight | numeric NOT NULL DEFAULT 1.0 |
| created_at | timestamp with time zone DEFAULT now() |

**Foreign Keys:**
- `review_category_scores.review_id` → `reviews.id`

**Indexes:**
- `idx_review_category_scores_category_id` (CREATE INDEX idx_review_category_scores_category_id ON public.review_category_scores USING btree (category_id))
- `idx_review_category_scores_question_id` (CREATE INDEX idx_review_category_scores_question_id ON public.review_category_scores USING btree (question_id))
- `idx_review_category_scores_review_id` (CREATE INDEX idx_review_category_scores_review_id ON public.review_category_scores USING btree (review_id))
- `review_category_scores_pkey` (CREATE UNIQUE INDEX review_category_scores_pkey ON public.review_category_scores USING btree (id))

---

## Relationships Summary

### High Level Relationships
- **users** 1 ⟶ ∞ **user_sessions**
- **freight_forwarders** 1 ⟶ ∞ **branches**
- **users** 1 ⟶ ∞ **reviews**
- **branches** 1 ⟶ ∞ **reviews**
- **freight_forwarders** 1 ⟶ ∞ **reviews**
- **reviews** 1 ⟶ ∞ **review_category_scores**
- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)
- **users** 1 ⟶ ∞ **disputes**
- **reviews** 1 ⟶ ∞ **disputes**
- **freight_forwarders** 1 ⟶ ∞ **disputes**
- **users** 1 ⟶ ∞ **disputes (resolved_by)**
- **freight_forwarders** 1 ⟶ ∞ **campaigns**

### Key Notes
- A review belongs to both a **branch** and the parent **freight_forwarder**
- **review_category_scores** stores individual question ratings (35 questions per review)
- **review_questions** serves as a reference table for current question set and rating criteria
- Disputes can be filed by a user and optionally resolved by another user
- The structure supports detailed analytics on individual question performance

## Export Information
- **Total Tables:** 1
- **Total Columns:** 10
- **Total Live Rows:** 0
- **Export Date:** 2025-08-14 01:51:16.80389+00
- **Database:** LogiScore Backend v0|
| # LogiScore Database Schema Export

Generated on: 2025-08-14 01:51:16.80389+00

## Tables Overview

| Table | Columns | Live Rows | Relationships |
|-------|---------|-----------|--------------|
| `review_questions` | 9 | 34 | No |

## Detailed Schema

### `review_questions`

**Columns:** 9

| Column | Type |
|--------|------|
| id | uuid NOT NULL DEFAULT gen_random_uuid() |
| category_id | character varying NOT NULL |
| category_name | character varying NOT NULL |
| question_id | character varying NOT NULL |
| question_text | text NOT NULL |
| rating_definitions | jsonb NOT NULL |
| is_active | boolean DEFAULT true |
| created_at | timestamp with time zone DEFAULT now() |
| updated_at | timestamp with time zone DEFAULT now() |

**Indexes:**
- `idx_review_questions_active` (CREATE INDEX idx_review_questions_active ON public.review_questions USING btree (is_active))
- `idx_review_questions_category_id` (CREATE INDEX idx_review_questions_category_id ON public.review_questions USING btree (category_id))
- `idx_review_questions_question_id` (CREATE INDEX idx_review_questions_question_id ON public.review_questions USING btree (question_id))
- `review_questions_pkey` (CREATE UNIQUE INDEX review_questions_pkey ON public.review_questions USING btree (id))
- `review_questions_question_id_key` (CREATE UNIQUE INDEX review_questions_question_id_key ON public.review_questions USING btree (question_id))

**Statistics:** 34 live rows, 34 total inserts

---

## Relationships Summary

### High Level Relationships
- **users** 1 ⟶ ∞ **user_sessions**
- **freight_forwarders** 1 ⟶ ∞ **branches**
- **users** 1 ⟶ ∞ **reviews**
- **branches** 1 ⟶ ∞ **reviews**
- **freight_forwarders** 1 ⟶ ∞ **reviews**
- **reviews** 1 ⟶ ∞ **review_category_scores**
- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)
- **users** 1 ⟶ ∞ **disputes**
- **reviews** 1 ⟶ ∞ **disputes**
- **freight_forwarders** 1 ⟶ ∞ **disputes**
- **users** 1 ⟶ ∞ **disputes (resolved_by)**
- **freight_forwarders** 1 ⟶ ∞ **campaigns**

### Key Notes
- A review belongs to both a **branch** and the parent **freight_forwarder**
- **review_category_scores** stores individual question ratings (35 questions per review)
- **review_questions** serves as a reference table for current question set and rating criteria
- Disputes can be filed by a user and optionally resolved by another user
- The structure supports detailed analytics on individual question performance

## Export Information
- **Total Tables:** 1
- **Total Columns:** 9
- **Total Live Rows:** 34
- **Export Date:** 2025-08-14 01:51:16.80389+00
- **Database:** LogiScore Backend v0|
| # LogiScore Database Schema Export

Generated on: 2025-08-14 01:51:16.80389+00

## Tables Overview

| Table | Columns | Live Rows | Relationships |
|-------|---------|-----------|--------------|
| `reviews` | 14 | 0 | Yes |

## Detailed Schema

### `reviews`

**Columns:** 14

| Column | Type |
|--------|------|
| id | uuid NOT NULL DEFAULT uuid_generate_v4() |
| user_id | uuid |
| branch_id | uuid |
| freight_forwarder_id | uuid |
| is_anonymous | boolean DEFAULT false |
| is_verified | boolean DEFAULT false |
| is_active | boolean DEFAULT true |
| created_at | timestamp with time zone DEFAULT now() |
| updated_at | timestamp with time zone DEFAULT now() |
| review_type | character varying DEFAULT 'general'::character varying |
| review_weight | numeric DEFAULT 1.0 |
| aggregate_rating | numeric |
| weighted_rating | numeric |
| total_questions_rated | integer(32,0) DEFAULT 0 |

**Foreign Keys:**
- `reviews.branch_id` → `branches.id`
- `reviews.freight_forwarder_id` → `freight_forwarders.id`
- `reviews.user_id` → `users.id`

**Indexes:**
- `idx_reviews_branch_id` (CREATE INDEX idx_reviews_branch_id ON public.reviews USING btree (branch_id))
- `idx_reviews_created_at` (CREATE INDEX idx_reviews_created_at ON public.reviews USING btree (created_at))
- `idx_reviews_freight_forwarder_id` (CREATE INDEX idx_reviews_freight_forwarder_id ON public.reviews USING btree (freight_forwarder_id))
- `reviews_pkey` (CREATE UNIQUE INDEX reviews_pkey ON public.reviews USING btree (id))

---

## Relationships Summary

### High Level Relationships
- **users** 1 ⟶ ∞ **user_sessions**
- **freight_forwarders** 1 ⟶ ∞ **branches**
- **users** 1 ⟶ ∞ **reviews**
- **branches** 1 ⟶ ∞ **reviews**
- **freight_forwarders** 1 ⟶ ∞ **reviews**
- **reviews** 1 ⟶ ∞ **review_category_scores**
- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)
- **users** 1 ⟶ ∞ **disputes**
- **reviews** 1 ⟶ ∞ **disputes**
- **freight_forwarders** 1 ⟶ ∞ **disputes**
- **users** 1 ⟶ ∞ **disputes (resolved_by)**
- **freight_forwarders** 1 ⟶ ∞ **campaigns**

### Key Notes
- A review belongs to both a **branch** and the parent **freight_forwarder**
- **review_category_scores** stores individual question ratings (35 questions per review)
- **review_questions** serves as a reference table for current question set and rating criteria
- Disputes can be filed by a user and optionally resolved by another user
- The structure supports detailed analytics on individual question performance

## Export Information
- **Total Tables:** 1
- **Total Columns:** 14
- **Total Live Rows:** 0
- **Export Date:** 2025-08-14 01:51:16.80389+00
- **Database:** LogiScore Backend v0|
| # LogiScore Database Schema Export

Generated on: 2025-08-14 01:51:16.80389+00

## Tables Overview

| Table | Columns | Live Rows | Relationships |
|-------|---------|-----------|--------------|
| `user_sessions` | 8 | 0 | Yes |

## Detailed Schema

### `user_sessions`

**Columns:** 8

| Column | Type |
|--------|------|
| id | uuid NOT NULL DEFAULT uuid_generate_v4() |
| user_id | uuid |
| session_token | character varying(255) NOT NULL |
| ip_address | inet |
| user_agent | text |
| is_active | boolean DEFAULT true |
| expires_at | timestamp with time zone NOT NULL |
| created_at | timestamp with time zone DEFAULT now() |

**Foreign Keys:**
- `user_sessions.user_id` → `users.id`

**Indexes:**
- `idx_user_sessions_token` (CREATE INDEX idx_user_sessions_token ON public.user_sessions USING btree (session_token))
- `idx_user_sessions_user_id` (CREATE INDEX idx_user_sessions_user_id ON public.user_sessions USING btree (user_id))
- `user_sessions_pkey` (CREATE UNIQUE INDEX user_sessions_pkey ON public.user_sessions USING btree (id))
- `user_sessions_session_token_key` (CREATE UNIQUE INDEX user_sessions_session_token_key ON public.user_sessions USING btree (session_token))

---

## Relationships Summary

### High Level Relationships
- **users** 1 ⟶ ∞ **user_sessions**
- **freight_forwarders** 1 ⟶ ∞ **branches**
- **users** 1 ⟶ ∞ **reviews**
- **branches** 1 ⟶ ∞ **reviews**
- **freight_forwarders** 1 ⟶ ∞ **reviews**
- **reviews** 1 ⟶ ∞ **review_category_scores**
- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)
- **users** 1 ⟶ ∞ **disputes**
- **reviews** 1 ⟶ ∞ **disputes**
- **freight_forwarders** 1 ⟶ ∞ **disputes**
- **users** 1 ⟶ ∞ **disputes (resolved_by)**
- **freight_forwarders** 1 ⟶ ∞ **campaigns**

### Key Notes
- A review belongs to both a **branch** and the parent **freight_forwarder**
- **review_category_scores** stores individual question ratings (35 questions per review)
- **review_questions** serves as a reference table for current question set and rating criteria
- Disputes can be filed by a user and optionally resolved by another user
- The structure supports detailed analytics on individual question performance

## Export Information
- **Total Tables:** 1
- **Total Columns:** 8
- **Total Live Rows:** 0
- **Export Date:** 2025-08-14 01:51:16.80389+00
- **Database:** LogiScore Backend v0|
| # LogiScore Database Schema Export

Generated on: 2025-08-14 01:51:16.80389+00

## Tables Overview

| Table | Columns | Live Rows | Relationships |
|-------|---------|-----------|--------------|
| `users` | 54 | 13 | No |

## Detailed Schema

### `users`

**Columns:** 54

| Column | Type |
|--------|------|
| id | uuid NOT NULL DEFAULT uuid_generate_v4() |
| instance_id | uuid |
| id | uuid NOT NULL |
| github_id | character varying(255) |
| aud | character varying(255) |
| email | character varying(255) NOT NULL |
| username | character varying(100) |
| role | character varying(255) |
| full_name | character varying(255) |
| email | character varying(255) |
| encrypted_password | character varying(255) |
| avatar_url | text |
| company_name | character varying(255) |
| email_confirmed_at | timestamp with time zone |
| user_type | character varying(20) DEFAULT 'shipper'::character varying |
| invited_at | timestamp with time zone |
| subscription_tier | character varying(20) DEFAULT 'free'::character varying |
| confirmation_token | character varying(255) |
| confirmation_sent_at | timestamp with time zone |
| stripe_customer_id | character varying(255) |
| recovery_token | character varying(255) |
| is_verified | boolean DEFAULT false |
| recovery_sent_at | timestamp with time zone |
| is_active | boolean DEFAULT true |
| created_at | timestamp with time zone DEFAULT now() |
| email_change_token_new | character varying(255) |
| updated_at | timestamp with time zone DEFAULT now() |
| email_change | character varying(255) |
| hashed_password | character varying(255) |
| email_change_sent_at | timestamp with time zone |
| reset_token | character varying(255) |
| last_sign_in_at | timestamp with time zone |
| raw_app_meta_data | jsonb |
| reset_token_expires | timestamp with time zone |
| verification_code | character varying(6) |
| raw_user_meta_data | jsonb |
| is_super_admin | boolean |
| verification_code_expires | timestamp with time zone |
| created_at | timestamp with time zone |
| updated_at | timestamp with time zone |
| phone | text DEFAULT NULL::character varying |
| phone_confirmed_at | timestamp with time zone |
| phone_change | text DEFAULT ''::character varying |
| phone_change_token | character varying(255) DEFAULT ''::character varying |
| phone_change_sent_at | timestamp with time zone |
| confirmed_at | timestamp with time zone |
| email_change_token_current | character varying(255) DEFAULT ''::character varying |
| email_change_confirm_status | smallint(16,0) DEFAULT 0 |
| banned_until | timestamp with time zone |
| reauthentication_token | character varying(255) DEFAULT ''::character varying |
| reauthentication_sent_at | timestamp with time zone |
| is_sso_user | boolean NOT NULL DEFAULT false |
| deleted_at | timestamp with time zone |
| is_anonymous | boolean NOT NULL DEFAULT false |

**Indexes:**
- `idx_users_email` (CREATE INDEX idx_users_email ON public.users USING btree (email))
- `idx_users_email_password` (CREATE INDEX idx_users_email_password ON public.users USING btree (email) WHERE (hashed_password IS NOT NULL))
- `idx_users_github_id` (CREATE INDEX idx_users_github_id ON public.users USING btree (github_id))
- `idx_users_reset_token` (CREATE INDEX idx_users_reset_token ON public.users USING btree (reset_token) WHERE (reset_token IS NOT NULL))
- `idx_users_verification_code` (CREATE INDEX idx_users_verification_code ON public.users USING btree (verification_code))
- `idx_users_verification_code_expires` (CREATE INDEX idx_users_verification_code_expires ON public.users USING btree (verification_code_expires))
- `users_email_key` (CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email))
- `users_github_id_key` (CREATE UNIQUE INDEX users_github_id_key ON public.users USING btree (github_id))
- `users_pkey` (CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id))
- `users_username_key` (CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username))

**Statistics:** 13 live rows, 16 total inserts

---

## Relationships Summary

### High Level Relationships
- **users** 1 ⟶ ∞ **user_sessions**
- **freight_forwarders** 1 ⟶ ∞ **branches**
- **users** 1 ⟶ ∞ **reviews**
- **branches** 1 ⟶ ∞ **reviews**
- **freight_forwarders** 1 ⟶ ∞ **reviews**
- **reviews** 1 ⟶ ∞ **review_category_scores**
- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)
- **users** 1 ⟶ ∞ **disputes**
- **reviews** 1 ⟶ ∞ **disputes**
- **freight_forwarders** 1 ⟶ ∞ **disputes**
- **users** 1 ⟶ ∞ **disputes (resolved_by)**
- **freight_forwarders** 1 ⟶ ∞ **campaigns**

### Key Notes
- A review belongs to both a **branch** and the parent **freight_forwarder**
- **review_category_scores** stores individual question ratings (35 questions per review)
- **review_questions** serves as a reference table for current question set and rating criteria
- Disputes can be filed by a user and optionally resolved by another user
- The structure supports detailed analytics on individual question performance

## Export Information
- **Total Tables:** 1
- **Total Columns:** 54
- **Total Live Rows:** 13
- **Export Date:** 2025-08-14 01:51:16.80389+00
- **Database:** LogiScore Backend v0 |