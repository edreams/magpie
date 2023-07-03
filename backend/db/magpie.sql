CREATE TABLE public.users (
 user_id serial PRIMARY KEY,   
 name text,  
 email text  
);   

CREATE TABLE public.user_links (  
 id serial PRIMARY KEY,
 user_id serial REFERENCES public.users (user_id) ON DELETE CASCADE,   
 link text,  
 FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE  
);      

CREATE TABLE public.summaries (  
 id serial PRIMARY KEY,     
 user_id serial REFERENCES public.users (user_id) ON DELETE CASCADE,
 link text,      
 summary text,  
 FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE  
);  

INSERT INTO users (user_id) VALUES (123);
