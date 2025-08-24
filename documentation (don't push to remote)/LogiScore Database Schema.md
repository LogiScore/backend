# LogiScore Complete Database Structure

Generated on: 2025-08-20 10:42:41.036188+00

## Database Overview

This document describes the complete database structure including tables, columns, indexes, and relationships.

## Tables

### ad_campaigns

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | uuid_generate_v4() |
| freight_forwarder_id | uuid | YES | N/A |
| campaign_name | character varying(255) | NO | N/A |
| campaign_type | character varying(50) | YES | N/A |
| start_date | date | NO | N/A |
| end_date | date | NO | N/A |
| budget | numeric(10,2) | YES | N/A |
| status | character varying(20) | YES | 'active'::character varying |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| ad_campaigns_pkey | CREATE UNIQUE INDEX ad_campaigns_pkey ON public.ad_campaigns USING btree (id) |

---


### disputes

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | uuid_generate_v4() |
| review_id | uuid | YES | N/A |
| user_id | uuid | YES | N/A |
| freight_forwarder_id | uuid | YES | N/A |
| dispute_type | character varying(50) | YES | N/A |
| description | text | NO | N/A |
| status | character varying(20) | YES | 'pending'::character varying |
| admin_notes | text | YES | N/A |
| reported_by | uuid | YES | N/A |
| resolved_at | timestamp with time zone | YES | N/A |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| disputes_pkey | CREATE UNIQUE INDEX disputes_pkey ON public.disputes USING btree (id) |
| idx_disputes_review_id | CREATE INDEX idx_disputes_review_id ON public.disputes USING btree (review_id) |
| idx_disputes_status | CREATE INDEX idx_disputes_status ON public.disputes USING btree (status) |

---


### freight_forwarders

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | uuid_generate_v4() |
| name | character varying(255) | NO | N/A |
| website | character varying(500) | YES | N/A |
| logo_url | text | YES | N/A |
| created_at | timestamp with time zone | YES | now() |
| description | text | YES | N/A |
| headquarters_country | character varying(255) | YES | N/A |
| global_rank | integer(32,0) | YES | N/A |
| is_active | boolean | YES | true |
| updated_at | timestamp with time zone | YES | now() |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| freight_forwarders_pkey | CREATE UNIQUE INDEX freight_forwarders_pkey ON public.freight_forwarders USING btree (id) |

---


### locations

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | integer(32,0) | NO | nextval('locations_id_seq'::regclass) |
| UUID | character varying(50) | NO | N/A |
| Location | character varying(500) | NO | N/A |
| City | character varying(200) | YES | N/A |
| State | character varying(200) | YES | N/A |
| Country | character varying(200) | NO | N/A |
| Region | character varying(200) | YES | N/A |
| Subregion | character varying(200) | YES | N/A |
| created_at | timestamp without time zone | YES | now() |
| updated_at | timestamp without time zone | YES | now() |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| idx_locations_city | CREATE INDEX idx_locations_city ON public.locations USING btree ("City") |
| idx_locations_city_country | CREATE INDEX idx_locations_city_country ON public.locations USING btree ("City", "Country") |
| idx_locations_country | CREATE INDEX idx_locations_country ON public.locations USING btree ("Country") |
| idx_locations_location | CREATE INDEX idx_locations_location ON public.locations USING btree ("Location") |
| idx_locations_region | CREATE INDEX idx_locations_region ON public.locations USING btree ("Region") |
| idx_locations_state | CREATE INDEX idx_locations_state ON public.locations USING btree ("State") |
| idx_locations_uuid | CREATE INDEX idx_locations_uuid ON public.locations USING btree ("UUID") |
| locations_UUID_key | CREATE UNIQUE INDEX "locations_UUID_key" ON public.locations USING btree ("UUID") |
| locations_pkey | CREATE UNIQUE INDEX locations_pkey ON public.locations USING btree (id) |

---


### review_category_scores

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| review_id | uuid | NO | N/A |
| category_id | character varying | NO | N/A |
| category_name | character varying | NO | N/A |
| question_id | character varying | NO | N/A |
| question_text | text | NO | N/A |
| rating | integer(32,0) | NO | N/A |
| rating_definition | text | YES | N/A |
| weight | numeric | NO | 1.0 |
| created_at | timestamp with time zone | YES | now() |
| category | character varying(100) | NO | N/A |
| score | double precision(53) | NO | N/A |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| idx_review_category_scores_category_id | CREATE INDEX idx_review_category_scores_category_id ON public.review_category_scores USING btree (category_id) |
| idx_review_category_scores_question_id | CREATE INDEX idx_review_category_scores_question_id ON public.review_category_scores USING btree (question_id) |
| idx_review_category_scores_review_id | CREATE INDEX idx_review_category_scores_review_id ON public.review_category_scores USING btree (review_id) |
| review_category_scores_pkey | CREATE UNIQUE INDEX review_category_scores_pkey ON public.review_category_scores USING btree (id) |

---


### review_questions

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | gen_random_uuid() |
| category_id | character varying | NO | N/A |
| category_name | character varying | NO | N/A |
| question_id | character varying | NO | N/A |
| question_text | text | NO | N/A |
| rating_definitions | jsonb | NO | N/A |
| is_active | boolean | YES | true |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| idx_review_questions_active | CREATE INDEX idx_review_questions_active ON public.review_questions USING btree (is_active) |
| idx_review_questions_category_id | CREATE INDEX idx_review_questions_category_id ON public.review_questions USING btree (category_id) |
| idx_review_questions_question_id | CREATE INDEX idx_review_questions_question_id ON public.review_questions USING btree (question_id) |
| review_questions_pkey | CREATE UNIQUE INDEX review_questions_pkey ON public.review_questions USING btree (id) |
| review_questions_question_id_key | CREATE UNIQUE INDEX review_questions_question_id_key ON public.review_questions USING btree (question_id) |

---


### reviews

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | uuid_generate_v4() |
| user_id | uuid | YES | N/A |
| branch_id | uuid | YES | N/A |
| freight_forwarder_id | uuid | YES | N/A |
| is_anonymous | boolean | YES | false |
| is_verified | boolean | YES | false |
| is_active | boolean | YES | true |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |
| review_type | character varying | YES | 'general'::character varying |
| review_weight | numeric | YES | 1.0 |
| aggregate_rating | numeric | YES | N/A |
| weighted_rating | numeric | YES | N/A |
| total_questions_rated | integer(32,0) | YES | 0 |
| city | character varying(100) | YES | N/A |
| country | character varying(100) | YES | N/A |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| idx_reviews_branch_id | CREATE INDEX idx_reviews_branch_id ON public.reviews USING btree (branch_id) |
| idx_reviews_city | CREATE INDEX idx_reviews_city ON public.reviews USING btree (city) |
| idx_reviews_city_country | CREATE INDEX idx_reviews_city_country ON public.reviews USING btree (city, country) |
| idx_reviews_country | CREATE INDEX idx_reviews_country ON public.reviews USING btree (country) |
| idx_reviews_created_at | CREATE INDEX idx_reviews_created_at ON public.reviews USING btree (created_at) |
| idx_reviews_freight_forwarder_id | CREATE INDEX idx_reviews_freight_forwarder_id ON public.reviews USING btree (freight_forwarder_id) |
| reviews_pkey | CREATE UNIQUE INDEX reviews_pkey ON public.reviews USING btree (id) |

---


### user_sessions

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | uuid_generate_v4() |
| user_id | uuid | YES | N/A |
| session_token | character varying(255) | NO | N/A |
| ip_address | inet | YES | N/A |
| user_agent | text | YES | N/A |
| is_active | boolean | YES | true |
| expires_at | timestamp with time zone | NO | N/A |
| created_at | timestamp with time zone | YES | now() |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| idx_user_sessions_token | CREATE INDEX idx_user_sessions_token ON public.user_sessions USING btree (session_token) |
| idx_user_sessions_user_id | CREATE INDEX idx_user_sessions_user_id ON public.user_sessions USING btree (user_id) |
| user_sessions_pkey | CREATE UNIQUE INDEX user_sessions_pkey ON public.user_sessions USING btree (id) |
| user_sessions_session_token_key | CREATE UNIQUE INDEX user_sessions_session_token_key ON public.user_sessions USING btree (session_token) |

---


### users

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NO | uuid_generate_v4() |
| instance_id | uuid | YES | N/A |
| id | uuid | NO | N/A |
| github_id | character varying(255) | YES | N/A |
| email | character varying(255) | NO | N/A |
| aud | character varying(255) | YES | N/A |
| username | character varying(100) | YES | N/A |
| role | character varying(255) | YES | N/A |
| full_name | character varying(255) | YES | N/A |
| email | character varying(255) | YES | N/A |
| avatar_url | text | YES | N/A |
| encrypted_password | character varying(255) | YES | N/A |
| email_confirmed_at | timestamp with time zone | YES | N/A |
| company_name | character varying(255) | YES | N/A |
| user_type | character varying(20) | YES | 'shipper'::character varying |
| invited_at | timestamp with time zone | YES | N/A |
| subscription_tier | character varying(20) | YES | 'free'::character varying |
| confirmation_token | character varying(255) | YES | N/A |
| stripe_customer_id | character varying(255) | YES | N/A |
| confirmation_sent_at | timestamp with time zone | YES | N/A |
| recovery_token | character varying(255) | YES | N/A |
| is_verified | boolean | YES | false |
| is_active | boolean | YES | true |
| recovery_sent_at | timestamp with time zone | YES | N/A |
| email_change_token_new | character varying(255) | YES | N/A |
| created_at | timestamp with time zone | YES | now() |
| updated_at | timestamp with time zone | YES | now() |
| email_change | character varying(255) | YES | N/A |
| email_change_sent_at | timestamp with time zone | YES | N/A |
| hashed_password | character varying(255) | YES | N/A |
| last_sign_in_at | timestamp with time zone | YES | N/A |
| reset_token | character varying(255) | YES | N/A |
| raw_app_meta_data | jsonb | YES | N/A |
| reset_token_expires | timestamp with time zone | YES | N/A |
| verification_code | character varying(6) | YES | N/A |
| raw_user_meta_data | jsonb | YES | N/A |
| is_super_admin | boolean | YES | N/A |
| verification_code_expires | timestamp with time zone | YES | N/A |
| created_at | timestamp with time zone | YES | N/A |
| updated_at | timestamp with time zone | YES | N/A |
| phone | text | YES | NULL::character varying |
| phone_confirmed_at | timestamp with time zone | YES | N/A |
| phone_change | text | YES | ''::character varying |
| phone_change_token | character varying(255) | YES | ''::character varying |
| phone_change_sent_at | timestamp with time zone | YES | N/A |
| confirmed_at | timestamp with time zone | YES | N/A |
| email_change_token_current | character varying(255) | YES | ''::character varying |
| email_change_confirm_status | smallint(16,0) | YES | 0 |
| banned_until | timestamp with time zone | YES | N/A |
| reauthentication_token | character varying(255) | YES | ''::character varying |
| reauthentication_sent_at | timestamp with time zone | YES | N/A |
| is_sso_user | boolean | NO | false |
| deleted_at | timestamp with time zone | YES | N/A |
| is_anonymous | boolean | NO | false |

**Indexes:**

| Index Name | Definition |
|-------------|------------|
| confirmation_token_idx | CREATE UNIQUE INDEX confirmation_token_idx ON auth.users USING btree (confirmation_token) WHERE ((confirmation_token)::text !~ '^[0-9 ]*$'::text) |
| email_change_token_current_idx | CREATE UNIQUE INDEX email_change_token_current_idx ON auth.users USING btree (email_change_token_current) WHERE ((email_change_token_current)::text !~ '^[0-9 ]*$'::text) |
| email_change_token_new_idx | CREATE UNIQUE INDEX email_change_token_new_idx ON auth.users USING btree (email_change_token_new) WHERE ((email_change_token_new)::text !~ '^[0-9 ]*$'::text) |
| idx_users_email | CREATE INDEX idx_users_email ON public.users USING btree (email) |
| idx_users_email_password | CREATE INDEX idx_users_email_password ON public.users USING btree (email) WHERE (hashed_password IS NOT NULL) |
| idx_users_github_id | CREATE INDEX idx_users_github_id ON public.users USING btree (github_id) |
| idx_users_reset_token | CREATE INDEX idx_users_reset_token ON public.users USING btree (reset_token) WHERE (reset_token IS NOT NULL) |
| idx_users_verification_code | CREATE INDEX idx_users_verification_code ON public.users USING btree (verification_code) |
| idx_users_verification_code_expires | CREATE INDEX idx_users_verification_code_expires ON public.users USING btree (verification_code_expires) |
| reauthentication_token_idx | CREATE UNIQUE INDEX reauthentication_token_idx ON auth.users USING btree (reauthentication_token) WHERE ((reauthentication_token)::text !~ '^[0-9 ]*$'::text) |
| recovery_token_idx | CREATE UNIQUE INDEX recovery_token_idx ON auth.users USING btree (recovery_token) WHERE ((recovery_token)::text !~ '^[0-9 ]*$'::text) |
| users_email_key | CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email) |
| users_email_partial_key | CREATE UNIQUE INDEX users_email_partial_key ON auth.users USING btree (email) WHERE (is_sso_user = false) |
| users_github_id_key | CREATE UNIQUE INDEX users_github_id_key ON public.users USING btree (github_id) |
| users_instance_id_email_idx | CREATE INDEX users_instance_id_email_idx ON auth.users USING btree (instance_id, lower((email)::text)) |
| users_instance_id_idx | CREATE INDEX users_instance_id_idx ON auth.users USING btree (instance_id) |
| users_is_anonymous_idx | CREATE INDEX users_is_anonymous_idx ON auth.users USING btree (is_anonymous) |
| users_phone_key | CREATE UNIQUE INDEX users_phone_key ON auth.users USING btree (phone) |
| users_pkey | CREATE UNIQUE INDEX users_pkey ON auth.users USING btree (id) |
| users_pkey | CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id) |
| users_username_key | CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username) |

---

## Database Relationships

### Foreign Key Relationships

| Table | Column | References | Referenced Column | Constraint Name |
|-------|--------|------------|-------------------|-----------------|
| ad_campaigns | freight_forwarder_id | freight_forwarders | id | ad_campaigns_freight_forwarder_id_fkey |
| disputes | freight_forwarder_id | freight_forwarders | id | disputes_freight_forwarder_id_fkey |
| disputes | reported_by | users | id | disputes_resolved_by_fkey |
| disputes | review_id | reviews | id | disputes_review_id_fkey |
| disputes | user_id | users | id | disputes_user_id_fkey |
| review_category_scores | review_id | reviews | id | review_category_scores_review_id_fkey |
| reviews | freight_forwarder_id | freight_forwarders | id | reviews_freight_forwarder_id_fkey |
| reviews | user_id | users | id | reviews_user_id_fkey |
| user_sessions | user_id | users | id | user_sessions_user_id_fkey |

### Relationship Diagram

- **ad_campaigns**.freight_forwarder_id → **freight_forwarders**.id (ad_campaigns_freight_forwarder_id_fkey)
- **disputes**.freight_forwarder_id → **freight_forwarders**.id (disputes_freight_forwarder_id_fkey)
- **disputes**.reported_by → **users**.id (disputes_resolved_by_fkey)
- **disputes**.review_id → **reviews**.id (disputes_review_id_fkey)
- **disputes**.user_id → **users**.id (disputes_user_id_fkey)
- **review_category_scores**.review_id → **reviews**.id (review_category_scores_review_id_fkey)
- **reviews**.freight_forwarder_id → **freight_forwarders**.id (reviews_freight_forwarder_id_fkey)
- **reviews**.user_id → **users**.id (reviews_user_id_fkey)
- **user_sessions**.user_id → **users**.id (user_sessions_user_id_fkey)

## Summary

- **Total Tables:** 9
- **Total Relationships:** 9
- **Schema:** public
- **Generated:** 2025-08-20 10:42:41.036188+00

## Notes

- All tables use the `public` schema
- Timestamps are in UTC
- Indexes are created for performance optimization
- Foreign keys ensure referential integrity

``` |