CREATE TABLE public.users (
    id serial PRIMARY KEY,
    name text,
    email text
);

CREATE TABLE public.summaries (
    id serial PRIMARY KEY,
    user_id integer,
    link text,
    summary text,
    FOREIGN KEY (user_id) REFERENCES public.users (id) ON DELETE CASCADE
);

CREATE TABLE public.user_links (
    id serial PRIMARY KEY,
    user_id integer,
    link text,
    FOREIGN KEY (user_id) REFERENCES public.users (id) ON DELETE CASCADE
);

