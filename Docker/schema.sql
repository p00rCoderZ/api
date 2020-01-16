--
-- PostgreSQL database dump
--

-- Dumped from database version 12.1 (Debian 12.1-1.pgdg100+1)
-- Dumped by pg_dump version 12.1 (Debian 12.1-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: post_status; Type: TYPE; Schema: public; Owner: pros
--

CREATE TYPE public.post_status AS ENUM (
    'active',
    'inactive'
);


ALTER TYPE public.post_status OWNER TO pros;

--
-- Name: post_type; Type: TYPE; Schema: public; Owner: pros
--

CREATE TYPE public.post_type AS ENUM (
    'offer',
    'seek'
);


ALTER TYPE public.post_type OWNER TO pros;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: post_tags; Type: TABLE; Schema: public; Owner: pros
--

CREATE TABLE public.post_tags (
    id integer NOT NULL,
    post_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.post_tags OWNER TO pros;

--
-- Name: post_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: pros
--

CREATE SEQUENCE public.post_tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.post_tags_id_seq OWNER TO pros;

--
-- Name: post_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pros
--

ALTER SEQUENCE public.post_tags_id_seq OWNED BY public.post_tags.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: pros
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    type public.post_type DEFAULT 'offer'::public.post_type NOT NULL,
    title character varying NOT NULL,
    content character varying NOT NULL,
    status public.post_status DEFAULT 'active'::public.post_status NOT NULL,
    datetime timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.posts OWNER TO pros;

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: pros
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posts_id_seq OWNER TO pros;

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pros
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: tags; Type: TABLE; Schema: public; Owner: pros
--

CREATE TABLE public.tags (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying
);


ALTER TABLE public.tags OWNER TO pros;

--
-- Name: tags_id_seq; Type: SEQUENCE; Schema: public; Owner: pros
--

CREATE SEQUENCE public.tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tags_id_seq OWNER TO pros;

--
-- Name: tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pros
--

ALTER SEQUENCE public.tags_id_seq OWNED BY public.tags.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: pros
--

CREATE TABLE public.users (
    id integer NOT NULL,
    nick character varying NOT NULL,
    name character varying,
    surname character varying,
    email character varying NOT NULL,
    password character varying NOT NULL,
    soft_delete boolean DEFAULT false NOT NULL
);


ALTER TABLE public.users OWNER TO pros;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: pros
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO pros;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pros
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: post_tags id; Type: DEFAULT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.post_tags ALTER COLUMN id SET DEFAULT nextval('public.post_tags_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: tags id; Type: DEFAULT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.tags ALTER COLUMN id SET DEFAULT nextval('public.tags_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: post_tags; Type: TABLE DATA; Schema: public; Owner: pros
--

COPY public.post_tags (id, post_id, tag_id) FROM stdin;
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: pros
--

COPY public.posts (id, user_id, type, title, content, status, datetime) FROM stdin;
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: pros
--

COPY public.tags (id, name, description) FROM stdin;
1	informatyka	Szeroko rozumiane pojecie informatyki
2	programowanie	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: pros
--

COPY public.users (id, nick, name, surname, email, password, soft_delete) FROM stdin;
\.


--
-- Name: post_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pros
--

SELECT pg_catalog.setval('public.post_tags_id_seq', 1, false);


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pros
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- Name: tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pros
--

SELECT pg_catalog.setval('public.tags_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pros
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: post_tags post_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.post_tags
    ADD CONSTRAINT post_tags_pkey PRIMARY KEY (id);


--
-- Name: post_tags post_tags_post_id_tag_id_key; Type: CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.post_tags
    ADD CONSTRAINT post_tags_post_id_tag_id_key UNIQUE (post_id, tag_id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: tags tags_name_key; Type: CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_name_key UNIQUE (name);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_nick_key; Type: CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_nick_key UNIQUE (nick);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: post_tags post_tags_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.post_tags
    ADD CONSTRAINT post_tags_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE;


--
-- Name: post_tags post_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.post_tags
    ADD CONSTRAINT post_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- Name: posts posts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pros
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

