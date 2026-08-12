--
-- PostgreSQL database dump
--

\restrict IgcYQbm8qiSi8xqihPuvOFQCGxxLhIaO5C0MxpxjmMoWu99SmxokJl50uoQzWgJ

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: adhesion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.adhesion (
    adhesion_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operator_id integer NOT NULL,
    remark text,
    rubber numeric,
    copper numeric,
    wood numeric,
    aluminium numeric,
    aluminium_anod numeric,
    lead numeric,
    rvs numeric,
    concrete numeric,
    glass numeric,
    pvc numeric,
    pmma numeric,
    pc numeric
);


--
-- Name: adhesion_adhesion_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.adhesion ALTER COLUMN adhesion_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.adhesion_adhesion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: adhesion_preparation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.adhesion_preparation (
    adhesion_preparation_id integer NOT NULL,
    sample_id integer NOT NULL,
    prepared_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    operator_id integer,
    remark text
);


--
-- Name: adhesion_preparation_adhesion_preparation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.adhesion_preparation_adhesion_preparation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: adhesion_preparation_adhesion_preparation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.adhesion_preparation_adhesion_preparation_id_seq OWNED BY public.adhesion_preparation.adhesion_preparation_id;


--
-- Name: after_storage; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.after_storage (
    afterstorage_id integer NOT NULL,
    sample_id integer NOT NULL,
    placed_in_oven_at timestamp without time zone,
    oven_location text,
    removed_from_oven timestamp without time zone,
    remark text
);


--
-- Name: after_storage_afterstorage_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.after_storage_afterstorage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: after_storage_afterstorage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.after_storage_afterstorage_id_seq OWNED BY public.after_storage.afterstorage_id;


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log (
    audit_id integer NOT NULL,
    table_name character varying(100) NOT NULL,
    record_id integer NOT NULL,
    changed_by integer,
    changed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    old_values jsonb,
    new_values jsonb,
    reason text
);


--
-- Name: audit_log_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.audit_log_audit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_log_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.audit_log_audit_id_seq OWNED BY public.audit_log.audit_id;


--
-- Name: curability; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.curability (
    cureability_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operator_id integer NOT NULL,
    remark text,
    day_1 numeric,
    temp_day1 text,
    rh_day1 text,
    day_7 numeric,
    temp_day7 text,
    rh_day7 text,
    afterstorage_id integer
);


--
-- Name: curability_cureability_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.curability ALTER COLUMN cureability_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.curability_cureability_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: curability_preparation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.curability_preparation (
    curability_preparation_id integer NOT NULL,
    sample_id integer NOT NULL,
    operator_id integer NOT NULL,
    removed_24h_at timestamp without time zone,
    removed_7d_at timestamp without time zone,
    remark text,
    prepared_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    afterstorage_id integer
);


--
-- Name: curability_preparation_curability_preparation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.curability_preparation_curability_preparation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: curability_preparation_curability_preparation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.curability_preparation_curability_preparation_id_seq OWNED BY public.curability_preparation.curability_preparation_id;


--
-- Name: density; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.density (
    density_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operator_id integer NOT NULL,
    remark text,
    vessel_empty numeric,
    vessel_full numeric,
    vessel_volume numeric,
    density_product numeric
);


--
-- Name: density_density_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.density ALTER COLUMN density_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.density_density_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: epdm_adhesion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.epdm_adhesion (
    epdm_adhesion_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone NOT NULL,
    operator_id integer NOT NULL,
    remark text,
    europees numeric,
    trc numeric,
    carlisle numeric,
    rubber numeric,
    copper numeric,
    wood numeric,
    aluminium numeric,
    aluminium_anod numeric,
    lead numeric,
    rvs numeric,
    concrete numeric,
    glass numeric,
    pvc numeric,
    pmma numeric,
    pc numeric
);


--
-- Name: epdm_adhesion_epdm_adhesion_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.epdm_adhesion ALTER COLUMN epdm_adhesion_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.epdm_adhesion_epdm_adhesion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: epdm_adhesion_preparation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.epdm_adhesion_preparation (
    epdm_adhesion_preparation_id integer NOT NULL,
    sample_id integer NOT NULL,
    prepared_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    operator_id integer,
    remark text
);


--
-- Name: epdm_adhesion_preparation_epdm_adhesion_preparation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.epdm_adhesion_preparation_epdm_adhesion_preparation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: epdm_adhesion_preparation_epdm_adhesion_preparation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.epdm_adhesion_preparation_epdm_adhesion_preparation_id_seq OWNED BY public.epdm_adhesion_preparation.epdm_adhesion_preparation_id;


--
-- Name: initial_tack; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.initial_tack (
    initial_tack_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operator_id integer NOT NULL,
    remark text,
    area numeric,
    area_weight numeric,
    added_weight numeric,
    initial_tack numeric,
    humidity numeric
);


--
-- Name: initial_tack_initial_tack_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.initial_tack ALTER COLUMN initial_tack_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.initial_tack_initial_tack_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: product_test_requirements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_test_requirements (
    product_id integer NOT NULL,
    test_type_id integer NOT NULL,
    frequency integer DEFAULT 1
);


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    product_code integer,
    product_name character varying(50)
);


--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.products ALTER COLUMN product_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.products_product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: rheology; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rheology (
    rheology_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operator_id integer NOT NULL,
    remark text,
    yield_stress numeric,
    vis_at_1 numeric,
    vis_at_5 numeric,
    vis_at_10 numeric,
    humidity numeric,
    afterstorage_id integer
);


--
-- Name: rheology_rheology_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.rheology ALTER COLUMN rheology_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.rheology_rheology_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: samples; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.samples (
    sample_id integer NOT NULL,
    batch_nr character varying(20) NOT NULL,
    prod_date date NOT NULL,
    product_id integer NOT NULL,
    remark text,
    batch_sequence integer,
    after_storage_required boolean DEFAULT false
);


--
-- Name: samples_sample_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.samples ALTER COLUMN sample_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.samples_sample_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: shore_a; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shore_a (
    shore_a_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operator_id integer NOT NULL,
    remark text,
    shore_a_1 numeric,
    shore_a_2 numeric,
    shore_a_3 numeric,
    shore_a_avg numeric,
    temperature numeric,
    humidity numeric
);


--
-- Name: shore_a_preparation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shore_a_preparation (
    shore_a_preparation_id integer NOT NULL,
    sample_id integer NOT NULL,
    prepared_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    operator_id integer,
    remark text
);


--
-- Name: shore_a_preparation_shore_a_preparation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.shore_a_preparation_shore_a_preparation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: shore_a_preparation_shore_a_preparation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.shore_a_preparation_shore_a_preparation_id_seq OWNED BY public.shore_a_preparation.shore_a_preparation_id;


--
-- Name: shore_a_shore_a_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.shore_a ALTER COLUMN shore_a_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.shore_a_shore_a_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: skinformation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.skinformation (
    skinformation_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operator_id integer NOT NULL,
    remark text,
    skinformation_time numeric,
    temp_skinformation_time numeric,
    rh_skinformation_time numeric,
    tack_free_time numeric,
    temp_tack_free_time numeric,
    rh_tack_free_time numeric,
    afterstorage_id integer
);


--
-- Name: skinformation_skinformation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.skinformation ALTER COLUMN skinformation_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.skinformation_skinformation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tasks (
    task_id integer NOT NULL,
    sample_id integer NOT NULL,
    task_type character varying(50) NOT NULL,
    due_date timestamp without time zone NOT NULL,
    completed boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tasks_task_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tasks_task_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tasks_task_id_seq OWNED BY public.tasks.task_id;


--
-- Name: tensile_specimen; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tensile_specimen (
    specimen_id integer NOT NULL,
    sample_id integer CONSTRAINT tensile_specimen_tensile_strength_id_not_null NOT NULL,
    specimen_no integer NOT NULL,
    width_1 numeric,
    width_2 numeric,
    width_3 numeric,
    width_avg numeric,
    thickness_1 numeric,
    thickness_2 numeric,
    thickness_3 numeric,
    thickness_avg numeric,
    t_max numeric,
    e_max numeric,
    t_50 numeric,
    t_100 numeric,
    remark text
);


--
-- Name: tensile_specimen_specimen_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.tensile_specimen ALTER COLUMN specimen_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tensile_specimen_specimen_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tensile_strength; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tensile_strength (
    tensile_strength_id integer NOT NULL,
    sample_id integer NOT NULL,
    test_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operator_id integer NOT NULL,
    remark text
);


--
-- Name: tensile_strength_preparation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tensile_strength_preparation (
    tensile_strength_preparation_id integer CONSTRAINT tensile_strength_preparatio_tensile_strength_preparati_not_null NOT NULL,
    sample_id integer NOT NULL,
    prepared_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    operator_id integer,
    remark text
);


--
-- Name: tensile_strength_preparation_tensile_strength_preparation_i_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tensile_strength_preparation_tensile_strength_preparation_i_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tensile_strength_preparation_tensile_strength_preparation_i_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tensile_strength_preparation_tensile_strength_preparation_i_seq OWNED BY public.tensile_strength_preparation.tensile_strength_preparation_id;


--
-- Name: tensile_strength_tensile_strength_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.tensile_strength ALTER COLUMN tensile_strength_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tensile_strength_tensile_strength_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: test_run_samples; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_run_samples (
    test_run_sample_id integer NOT NULL,
    test_run_id integer NOT NULL,
    sample_id integer NOT NULL
);


--
-- Name: test_run_samples_test_run_sample_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.test_run_samples ALTER COLUMN test_run_sample_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.test_run_samples_test_run_sample_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: test_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_runs (
    test_run_id integer NOT NULL,
    test_type_id integer NOT NULL,
    test_date timestamp without time zone NOT NULL,
    operator_id integer NOT NULL,
    remark text
);


--
-- Name: test_runs_test_run_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.test_runs ALTER COLUMN test_run_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.test_runs_test_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: test_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_types (
    test_type_id integer NOT NULL,
    test_name character varying(50) NOT NULL
);


--
-- Name: test_types_test_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.test_types ALTER COLUMN test_type_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.test_types_test_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    name character varying(50) CONSTRAINT users_user_name_not_null NOT NULL,
    user_role character varying(20) NOT NULL,
    password_hash text,
    active boolean DEFAULT true,
    must_change_password boolean DEFAULT false,
    username character varying(50)
);


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users ALTER COLUMN user_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: adhesion_preparation adhesion_preparation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adhesion_preparation ALTER COLUMN adhesion_preparation_id SET DEFAULT nextval('public.adhesion_preparation_adhesion_preparation_id_seq'::regclass);


--
-- Name: after_storage afterstorage_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.after_storage ALTER COLUMN afterstorage_id SET DEFAULT nextval('public.after_storage_afterstorage_id_seq'::regclass);


--
-- Name: audit_log audit_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN audit_id SET DEFAULT nextval('public.audit_log_audit_id_seq'::regclass);


--
-- Name: curability_preparation curability_preparation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability_preparation ALTER COLUMN curability_preparation_id SET DEFAULT nextval('public.curability_preparation_curability_preparation_id_seq'::regclass);


--
-- Name: epdm_adhesion_preparation epdm_adhesion_preparation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.epdm_adhesion_preparation ALTER COLUMN epdm_adhesion_preparation_id SET DEFAULT nextval('public.epdm_adhesion_preparation_epdm_adhesion_preparation_id_seq'::regclass);


--
-- Name: shore_a_preparation shore_a_preparation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shore_a_preparation ALTER COLUMN shore_a_preparation_id SET DEFAULT nextval('public.shore_a_preparation_shore_a_preparation_id_seq'::regclass);


--
-- Name: tasks task_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks ALTER COLUMN task_id SET DEFAULT nextval('public.tasks_task_id_seq'::regclass);


--
-- Name: tensile_strength_preparation tensile_strength_preparation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_strength_preparation ALTER COLUMN tensile_strength_preparation_id SET DEFAULT nextval('public.tensile_strength_preparation_tensile_strength_preparation_i_seq'::regclass);


--
-- Name: adhesion adhesion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adhesion
    ADD CONSTRAINT adhesion_pkey PRIMARY KEY (adhesion_id);


--
-- Name: adhesion_preparation adhesion_preparation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adhesion_preparation
    ADD CONSTRAINT adhesion_preparation_pkey PRIMARY KEY (adhesion_preparation_id);


--
-- Name: after_storage after_storage_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.after_storage
    ADD CONSTRAINT after_storage_pkey PRIMARY KEY (afterstorage_id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (audit_id);


--
-- Name: curability curability_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability
    ADD CONSTRAINT curability_pkey PRIMARY KEY (cureability_id);


--
-- Name: curability_preparation curability_preparation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability_preparation
    ADD CONSTRAINT curability_preparation_pkey PRIMARY KEY (curability_preparation_id);


--
-- Name: density density_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.density
    ADD CONSTRAINT density_pkey PRIMARY KEY (density_id);


--
-- Name: epdm_adhesion epdm_adhesion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.epdm_adhesion
    ADD CONSTRAINT epdm_adhesion_pkey PRIMARY KEY (epdm_adhesion_id);


--
-- Name: epdm_adhesion_preparation epdm_adhesion_preparation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.epdm_adhesion_preparation
    ADD CONSTRAINT epdm_adhesion_preparation_pkey PRIMARY KEY (epdm_adhesion_preparation_id);


--
-- Name: initial_tack initial_tack_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.initial_tack
    ADD CONSTRAINT initial_tack_pkey PRIMARY KEY (initial_tack_id);


--
-- Name: product_test_requirements product_test_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_test_requirements
    ADD CONSTRAINT product_test_requirements_pkey PRIMARY KEY (product_id, test_type_id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: rheology rheology_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rheology
    ADD CONSTRAINT rheology_pkey PRIMARY KEY (rheology_id);


--
-- Name: samples samples_batch_nr_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.samples
    ADD CONSTRAINT samples_batch_nr_key UNIQUE (batch_nr);


--
-- Name: samples samples_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.samples
    ADD CONSTRAINT samples_pkey PRIMARY KEY (sample_id);


--
-- Name: shore_a shore_a_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shore_a
    ADD CONSTRAINT shore_a_pkey PRIMARY KEY (shore_a_id);


--
-- Name: shore_a_preparation shore_a_preparation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shore_a_preparation
    ADD CONSTRAINT shore_a_preparation_pkey PRIMARY KEY (shore_a_preparation_id);


--
-- Name: skinformation skinformation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skinformation
    ADD CONSTRAINT skinformation_pkey PRIMARY KEY (skinformation_id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (task_id);


--
-- Name: tensile_specimen tensile_specimen_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_specimen
    ADD CONSTRAINT tensile_specimen_pkey PRIMARY KEY (specimen_id);


--
-- Name: tensile_strength tensile_strength_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_strength
    ADD CONSTRAINT tensile_strength_pkey PRIMARY KEY (tensile_strength_id);


--
-- Name: tensile_strength_preparation tensile_strength_preparation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_strength_preparation
    ADD CONSTRAINT tensile_strength_preparation_pkey PRIMARY KEY (tensile_strength_preparation_id);


--
-- Name: test_run_samples test_run_samples_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_run_samples
    ADD CONSTRAINT test_run_samples_pkey PRIMARY KEY (test_run_sample_id);


--
-- Name: test_run_samples test_run_samples_test_run_id_sample_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_run_samples
    ADD CONSTRAINT test_run_samples_test_run_id_sample_id_key UNIQUE (test_run_id, sample_id);


--
-- Name: test_runs test_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_runs
    ADD CONSTRAINT test_runs_pkey PRIMARY KEY (test_run_id);


--
-- Name: test_types test_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_types
    ADD CONSTRAINT test_types_pkey PRIMARY KEY (test_type_id);


--
-- Name: test_types test_types_test_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_types
    ADD CONSTRAINT test_types_test_name_key UNIQUE (test_name);


--
-- Name: curability unique_curability_afterstorage; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability
    ADD CONSTRAINT unique_curability_afterstorage UNIQUE (afterstorage_id);


--
-- Name: rheology unique_rheology_afterstorage; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rheology
    ADD CONSTRAINT unique_rheology_afterstorage UNIQUE (afterstorage_id);


--
-- Name: skinformation unique_skinformation_afterstorage; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skinformation
    ADD CONSTRAINT unique_skinformation_afterstorage UNIQUE (afterstorage_id);


--
-- Name: rheology uq_rheology_sample; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rheology
    ADD CONSTRAINT uq_rheology_sample UNIQUE (sample_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_user_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_name_key UNIQUE (name);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: adhesion adhesion_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adhesion
    ADD CONSTRAINT adhesion_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: adhesion_preparation adhesion_preparation_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adhesion_preparation
    ADD CONSTRAINT adhesion_preparation_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: adhesion_preparation adhesion_preparation_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adhesion_preparation
    ADD CONSTRAINT adhesion_preparation_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: adhesion adhesion_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adhesion
    ADD CONSTRAINT adhesion_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: after_storage after_storage_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.after_storage
    ADD CONSTRAINT after_storage_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id) ON DELETE CASCADE;


--
-- Name: audit_log audit_log_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(user_id);


--
-- Name: curability curability_afterstorage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability
    ADD CONSTRAINT curability_afterstorage_id_fkey FOREIGN KEY (afterstorage_id) REFERENCES public.after_storage(afterstorage_id);


--
-- Name: curability curability_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability
    ADD CONSTRAINT curability_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: curability_preparation curability_preparation_afterstorage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability_preparation
    ADD CONSTRAINT curability_preparation_afterstorage_id_fkey FOREIGN KEY (afterstorage_id) REFERENCES public.after_storage(afterstorage_id);


--
-- Name: curability_preparation curability_preparation_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability_preparation
    ADD CONSTRAINT curability_preparation_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: curability_preparation curability_preparation_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability_preparation
    ADD CONSTRAINT curability_preparation_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: curability curability_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.curability
    ADD CONSTRAINT curability_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: density density_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.density
    ADD CONSTRAINT density_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: density density_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.density
    ADD CONSTRAINT density_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: epdm_adhesion epdm_adhesion_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.epdm_adhesion
    ADD CONSTRAINT epdm_adhesion_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: epdm_adhesion_preparation epdm_adhesion_preparation_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.epdm_adhesion_preparation
    ADD CONSTRAINT epdm_adhesion_preparation_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: epdm_adhesion_preparation epdm_adhesion_preparation_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.epdm_adhesion_preparation
    ADD CONSTRAINT epdm_adhesion_preparation_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: epdm_adhesion epdm_adhesion_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.epdm_adhesion
    ADD CONSTRAINT epdm_adhesion_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: initial_tack initial_tack_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.initial_tack
    ADD CONSTRAINT initial_tack_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: initial_tack initial_tack_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.initial_tack
    ADD CONSTRAINT initial_tack_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: product_test_requirements product_test_requirements_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_test_requirements
    ADD CONSTRAINT product_test_requirements_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: product_test_requirements product_test_requirements_test_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_test_requirements
    ADD CONSTRAINT product_test_requirements_test_type_id_fkey FOREIGN KEY (test_type_id) REFERENCES public.test_types(test_type_id);


--
-- Name: rheology rheology_afterstorage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rheology
    ADD CONSTRAINT rheology_afterstorage_id_fkey FOREIGN KEY (afterstorage_id) REFERENCES public.after_storage(afterstorage_id);


--
-- Name: rheology rheology_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rheology
    ADD CONSTRAINT rheology_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: rheology rheology_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rheology
    ADD CONSTRAINT rheology_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: samples samples_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.samples
    ADD CONSTRAINT samples_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: shore_a shore_a_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shore_a
    ADD CONSTRAINT shore_a_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: shore_a_preparation shore_a_preparation_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shore_a_preparation
    ADD CONSTRAINT shore_a_preparation_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: shore_a_preparation shore_a_preparation_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shore_a_preparation
    ADD CONSTRAINT shore_a_preparation_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: shore_a shore_a_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shore_a
    ADD CONSTRAINT shore_a_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: skinformation skinformation_afterstorage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skinformation
    ADD CONSTRAINT skinformation_afterstorage_id_fkey FOREIGN KEY (afterstorage_id) REFERENCES public.after_storage(afterstorage_id);


--
-- Name: skinformation skinformation_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skinformation
    ADD CONSTRAINT skinformation_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: skinformation skinformation_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skinformation
    ADD CONSTRAINT skinformation_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: tasks tasks_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: tensile_specimen tensile_specimen_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_specimen
    ADD CONSTRAINT tensile_specimen_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: tensile_strength tensile_strength_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_strength
    ADD CONSTRAINT tensile_strength_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: tensile_strength_preparation tensile_strength_preparation_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_strength_preparation
    ADD CONSTRAINT tensile_strength_preparation_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: tensile_strength_preparation tensile_strength_preparation_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_strength_preparation
    ADD CONSTRAINT tensile_strength_preparation_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: tensile_strength tensile_strength_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tensile_strength
    ADD CONSTRAINT tensile_strength_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: test_run_samples test_run_samples_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_run_samples
    ADD CONSTRAINT test_run_samples_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(sample_id);


--
-- Name: test_run_samples test_run_samples_test_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_run_samples
    ADD CONSTRAINT test_run_samples_test_run_id_fkey FOREIGN KEY (test_run_id) REFERENCES public.test_runs(test_run_id);


--
-- Name: test_runs test_runs_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_runs
    ADD CONSTRAINT test_runs_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.users(user_id);


--
-- Name: test_runs test_runs_test_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_runs
    ADD CONSTRAINT test_runs_test_type_id_fkey FOREIGN KEY (test_type_id) REFERENCES public.test_types(test_type_id);


--
-- PostgreSQL database dump complete
--

\unrestrict IgcYQbm8qiSi8xqihPuvOFQCGxxLhIaO5C0MxpxjmMoWu99SmxokJl50uoQzWgJ

