CREATE TABLE public.users (
 user_id bigserial PRIMARY KEY,
 name text,
 email text
);

CREATE TABLE public.user_links (
 id bigserial PRIMARY KEY,
 user_id bigint REFERENCES public.users (user_id) ON DELETE CASCADE,
 link text
);

CREATE TABLE public.summaries (
 id bigserial PRIMARY KEY,
 user_id bigint REFERENCES public.users (user_id) ON DELETE CASCADE,
 link text,
 type text,
 summary text,
 audio bytea
);
