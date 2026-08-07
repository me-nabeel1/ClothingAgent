--
-- PostgreSQL database dump
--

\restrict BL7CqmGhNfHWdHPaP2XXlmIecnvSlFRTmYvy7A3cePATptQm2hKt0CvZriqJzKf

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

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
-- Name: agent_runtime; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA agent_runtime;


ALTER SCHEMA agent_runtime OWNER TO postgres;

--
-- Name: clothing_store; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA clothing_store;


ALTER SCHEMA clothing_store OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cart_items; Type: TABLE; Schema: agent_runtime; Owner: postgres
--

CREATE TABLE agent_runtime.cart_items (
    cart_item_id uuid NOT NULL,
    cart_id uuid NOT NULL,
    product_id bigint NOT NULL,
    variant_id bigint NOT NULL,
    branch_id bigint NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT cart_items_quantity_check CHECK ((quantity > 0)),
    CONSTRAINT cart_items_unit_price_check CHECK ((unit_price >= (0)::numeric))
);


ALTER TABLE agent_runtime.cart_items OWNER TO postgres;

--
-- Name: carts; Type: TABLE; Schema: agent_runtime; Owner: postgres
--

CREATE TABLE agent_runtime.carts (
    cart_id uuid NOT NULL,
    session_id uuid NOT NULL,
    status character varying(30) DEFAULT 'ACTIVE'::character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE agent_runtime.carts OWNER TO postgres;

--
-- Name: conversation_messages; Type: TABLE; Schema: agent_runtime; Owner: postgres
--

CREATE TABLE agent_runtime.conversation_messages (
    message_id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE agent_runtime.conversation_messages OWNER TO postgres;

--
-- Name: conversations; Type: TABLE; Schema: agent_runtime; Owner: postgres
--

CREATE TABLE agent_runtime.conversations (
    conversation_id uuid NOT NULL,
    session_id uuid NOT NULL,
    status character varying(30) DEFAULT 'ACTIVE'::character varying NOT NULL,
    preferences jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE agent_runtime.conversations OWNER TO postgres;

--
-- Name: displayed_results; Type: TABLE; Schema: agent_runtime; Owner: postgres
--

CREATE TABLE agent_runtime.displayed_results (
    displayed_result_id uuid NOT NULL,
    conversation_id uuid NOT NULL,
    message_id uuid NOT NULL,
    "position" integer NOT NULL,
    product_id bigint NOT NULL,
    variant_id bigint NOT NULL,
    branch_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT displayed_results_position_check CHECK (("position" > 0))
);


ALTER TABLE agent_runtime.displayed_results OWNER TO postgres;

--
-- Name: order_items; Type: TABLE; Schema: agent_runtime; Owner: postgres
--

CREATE TABLE agent_runtime.order_items (
    order_item_id uuid NOT NULL,
    order_id uuid NOT NULL,
    product_id bigint NOT NULL,
    variant_id bigint NOT NULL,
    branch_id bigint NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    CONSTRAINT order_items_quantity_check CHECK ((quantity > 0)),
    CONSTRAINT order_items_unit_price_check CHECK ((unit_price >= (0)::numeric))
);


ALTER TABLE agent_runtime.order_items OWNER TO postgres;

--
-- Name: orders; Type: TABLE; Schema: agent_runtime; Owner: postgres
--

CREATE TABLE agent_runtime.orders (
    order_id uuid NOT NULL,
    session_id uuid NOT NULL,
    cart_id uuid NOT NULL,
    status character varying(40) DEFAULT 'PENDING_CONFIRMATION'::character varying NOT NULL,
    subtotal numeric(14,2) DEFAULT 0 NOT NULL,
    confirmation_expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    confirmed_at timestamp with time zone,
    CONSTRAINT orders_subtotal_check CHECK ((subtotal >= (0)::numeric))
);


ALTER TABLE agent_runtime.orders OWNER TO postgres;

--
-- Name: stock_reservations; Type: TABLE; Schema: agent_runtime; Owner: postgres
--

CREATE TABLE agent_runtime.stock_reservations (
    reservation_id uuid NOT NULL,
    order_id uuid NOT NULL,
    variant_id bigint NOT NULL,
    branch_id bigint NOT NULL,
    quantity integer NOT NULL,
    status character varying(30) DEFAULT 'ACTIVE'::character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    CONSTRAINT stock_reservations_quantity_check CHECK ((quantity > 0))
);


ALTER TABLE agent_runtime.stock_reservations OWNER TO postgres;

--
-- Name: branch_inventory; Type: TABLE; Schema: clothing_store; Owner: postgres
--

CREATE TABLE clothing_store.branch_inventory (
    inventory_id bigint NOT NULL,
    branch_id bigint NOT NULL,
    variant_id bigint NOT NULL,
    quantity_on_hand integer DEFAULT 0 NOT NULL,
    reserved_quantity integer DEFAULT 0 NOT NULL,
    damaged_quantity integer DEFAULT 0 NOT NULL,
    in_transit_quantity integer DEFAULT 0 NOT NULL,
    reorder_level integer DEFAULT 0 NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT branch_inventory_check CHECK (((reserved_quantity + damaged_quantity) <= quantity_on_hand)),
    CONSTRAINT branch_inventory_damaged_quantity_check CHECK ((damaged_quantity >= 0)),
    CONSTRAINT branch_inventory_in_transit_quantity_check CHECK ((in_transit_quantity >= 0)),
    CONSTRAINT branch_inventory_quantity_on_hand_check CHECK ((quantity_on_hand >= 0)),
    CONSTRAINT branch_inventory_reorder_level_check CHECK ((reorder_level >= 0)),
    CONSTRAINT branch_inventory_reserved_quantity_check CHECK ((reserved_quantity >= 0))
);


ALTER TABLE clothing_store.branch_inventory OWNER TO postgres;

--
-- Name: branch_inventory_inventory_id_seq; Type: SEQUENCE; Schema: clothing_store; Owner: postgres
--

CREATE SEQUENCE clothing_store.branch_inventory_inventory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE clothing_store.branch_inventory_inventory_id_seq OWNER TO postgres;

--
-- Name: branch_inventory_inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: clothing_store; Owner: postgres
--

ALTER SEQUENCE clothing_store.branch_inventory_inventory_id_seq OWNED BY clothing_store.branch_inventory.inventory_id;


--
-- Name: branches; Type: TABLE; Schema: clothing_store; Owner: postgres
--

CREATE TABLE clothing_store.branches (
    branch_id bigint NOT NULL,
    branch_code character varying(20) NOT NULL,
    branch_name character varying(120) NOT NULL,
    city character varying(80) NOT NULL,
    address text DEFAULT ''::text NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE clothing_store.branches OWNER TO postgres;

--
-- Name: branches_branch_id_seq; Type: SEQUENCE; Schema: clothing_store; Owner: postgres
--

CREATE SEQUENCE clothing_store.branches_branch_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE clothing_store.branches_branch_id_seq OWNER TO postgres;

--
-- Name: branches_branch_id_seq; Type: SEQUENCE OWNED BY; Schema: clothing_store; Owner: postgres
--

ALTER SEQUENCE clothing_store.branches_branch_id_seq OWNED BY clothing_store.branches.branch_id;


--
-- Name: categories; Type: TABLE; Schema: clothing_store; Owner: postgres
--

CREATE TABLE clothing_store.categories (
    category_id bigint NOT NULL,
    parent_category_id bigint,
    category_name character varying(100) NOT NULL,
    category_code character varying(50) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE clothing_store.categories OWNER TO postgres;

--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: clothing_store; Owner: postgres
--

CREATE SEQUENCE clothing_store.categories_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE clothing_store.categories_category_id_seq OWNER TO postgres;

--
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: clothing_store; Owner: postgres
--

ALTER SEQUENCE clothing_store.categories_category_id_seq OWNED BY clothing_store.categories.category_id;


--
-- Name: colors; Type: TABLE; Schema: clothing_store; Owner: postgres
--

CREATE TABLE clothing_store.colors (
    color_id bigint NOT NULL,
    color_name character varying(60) NOT NULL,
    color_code character varying(40) NOT NULL,
    hex_code character varying(7)
);


ALTER TABLE clothing_store.colors OWNER TO postgres;

--
-- Name: colors_color_id_seq; Type: SEQUENCE; Schema: clothing_store; Owner: postgres
--

CREATE SEQUENCE clothing_store.colors_color_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE clothing_store.colors_color_id_seq OWNER TO postgres;

--
-- Name: colors_color_id_seq; Type: SEQUENCE OWNED BY; Schema: clothing_store; Owner: postgres
--

ALTER SEQUENCE clothing_store.colors_color_id_seq OWNED BY clothing_store.colors.color_id;


--
-- Name: product_images; Type: TABLE; Schema: clothing_store; Owner: postgres
--

CREATE TABLE clothing_store.product_images (
    image_id bigint NOT NULL,
    product_id bigint NOT NULL,
    image_path text NOT NULL,
    alt_text character varying(250),
    display_order integer DEFAULT 1 NOT NULL,
    is_primary boolean DEFAULT false NOT NULL,
    color_id integer
);


ALTER TABLE clothing_store.product_images OWNER TO postgres;

--
-- Name: product_images_image_id_seq; Type: SEQUENCE; Schema: clothing_store; Owner: postgres
--

CREATE SEQUENCE clothing_store.product_images_image_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE clothing_store.product_images_image_id_seq OWNER TO postgres;

--
-- Name: product_images_image_id_seq; Type: SEQUENCE OWNED BY; Schema: clothing_store; Owner: postgres
--

ALTER SEQUENCE clothing_store.product_images_image_id_seq OWNED BY clothing_store.product_images.image_id;


--
-- Name: product_variants; Type: TABLE; Schema: clothing_store; Owner: postgres
--

CREATE TABLE clothing_store.product_variants (
    variant_id bigint NOT NULL,
    product_id bigint NOT NULL,
    color_id bigint NOT NULL,
    size_id bigint NOT NULL,
    sku character varying(80) NOT NULL,
    barcode character varying(20),
    cost_price numeric(12,2) DEFAULT 0 NOT NULL,
    selling_price numeric(12,2) DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT product_variants_cost_price_check CHECK ((cost_price >= (0)::numeric)),
    CONSTRAINT product_variants_selling_price_check CHECK ((selling_price >= (0)::numeric))
);


ALTER TABLE clothing_store.product_variants OWNER TO postgres;

--
-- Name: product_variants_variant_id_seq; Type: SEQUENCE; Schema: clothing_store; Owner: postgres
--

CREATE SEQUENCE clothing_store.product_variants_variant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE clothing_store.product_variants_variant_id_seq OWNER TO postgres;

--
-- Name: product_variants_variant_id_seq; Type: SEQUENCE OWNED BY; Schema: clothing_store; Owner: postgres
--

ALTER SEQUENCE clothing_store.product_variants_variant_id_seq OWNED BY clothing_store.product_variants.variant_id;


--
-- Name: products; Type: TABLE; Schema: clothing_store; Owner: postgres
--

CREATE TABLE clothing_store.products (
    product_id bigint NOT NULL,
    article_code character varying(40) NOT NULL,
    product_name character varying(180) NOT NULL,
    category_id bigint NOT NULL,
    gender character varying(20) DEFAULT 'UNISEX'::character varying NOT NULL,
    brand character varying(100) DEFAULT ''::character varying NOT NULL,
    material character varying(160),
    fit character varying(60),
    season character varying(80),
    base_cost_price numeric(12,2) DEFAULT 0 NOT NULL,
    base_selling_price numeric(12,2) DEFAULT 0 NOT NULL,
    product_status character varying(30) DEFAULT 'ACTIVE'::character varying NOT NULL,
    availability_scope character varying(40) DEFAULT 'ALL_BRANCHES'::character varying NOT NULL,
    description text,
    search_tags jsonb DEFAULT '[]'::jsonb NOT NULL,
    CONSTRAINT products_base_cost_price_check CHECK ((base_cost_price >= (0)::numeric)),
    CONSTRAINT products_base_selling_price_check CHECK ((base_selling_price >= (0)::numeric))
);


ALTER TABLE clothing_store.products OWNER TO postgres;

--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: clothing_store; Owner: postgres
--

CREATE SEQUENCE clothing_store.products_product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE clothing_store.products_product_id_seq OWNER TO postgres;

--
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: clothing_store; Owner: postgres
--

ALTER SEQUENCE clothing_store.products_product_id_seq OWNED BY clothing_store.products.product_id;


--
-- Name: sizes; Type: TABLE; Schema: clothing_store; Owner: postgres
--

CREATE TABLE clothing_store.sizes (
    size_id bigint NOT NULL,
    size_label character varying(20) NOT NULL,
    size_type character varying(30) NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL
);


ALTER TABLE clothing_store.sizes OWNER TO postgres;

--
-- Name: sizes_size_id_seq; Type: SEQUENCE; Schema: clothing_store; Owner: postgres
--

CREATE SEQUENCE clothing_store.sizes_size_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE clothing_store.sizes_size_id_seq OWNER TO postgres;

--
-- Name: sizes_size_id_seq; Type: SEQUENCE OWNED BY; Schema: clothing_store; Owner: postgres
--

ALTER SEQUENCE clothing_store.sizes_size_id_seq OWNED BY clothing_store.sizes.size_id;


--
-- Name: v_inventory_catalog; Type: VIEW; Schema: clothing_store; Owner: postgres
--

CREATE VIEW clothing_store.v_inventory_catalog AS
 SELECT p.product_id,
    p.article_code,
    p.product_name,
    c.category_name,
    p.brand,
    p.material,
    p.fit,
    p.season,
    p.search_tags,
    pv.variant_id,
    pv.sku,
    co.color_name,
    s.size_label,
    pv.selling_price,
    b.branch_id,
    b.branch_code,
    b.branch_name,
    b.city,
    GREATEST(((bi.quantity_on_hand - bi.reserved_quantity) - bi.damaged_quantity), 0) AS available_quantity,
    bi.in_transit_quantity,
        CASE
            WHEN (((bi.quantity_on_hand - bi.reserved_quantity) - bi.damaged_quantity) > 0) THEN 'IN_STOCK'::text
            WHEN (bi.in_transit_quantity > 0) THEN 'OUT_OF_STOCK_IN_TRANSIT'::text
            ELSE 'OUT_OF_STOCK'::text
        END AS stock_status,
    pi.image_path
   FROM (((((((clothing_store.products p
     JOIN clothing_store.categories c ON ((c.category_id = p.category_id)))
     JOIN clothing_store.product_variants pv ON ((pv.product_id = p.product_id)))
     JOIN clothing_store.colors co ON ((co.color_id = pv.color_id)))
     JOIN clothing_store.sizes s ON ((s.size_id = pv.size_id)))
     JOIN clothing_store.branch_inventory bi ON ((bi.variant_id = pv.variant_id)))
     JOIN clothing_store.branches b ON ((b.branch_id = bi.branch_id)))
     LEFT JOIN clothing_store.product_images pi ON (((pi.product_id = p.product_id) AND (pi.is_primary = true))))
  WHERE (((p.product_status)::text = 'ACTIVE'::text) AND (pv.is_active = true) AND (b.is_active = true));


ALTER VIEW clothing_store.v_inventory_catalog OWNER TO postgres;

--
-- Name: v_low_stock; Type: VIEW; Schema: clothing_store; Owner: postgres
--

CREATE VIEW clothing_store.v_low_stock AS
 SELECT product_id,
    article_code,
    product_name,
    category_name,
    brand,
    material,
    fit,
    season,
    search_tags,
    variant_id,
    sku,
    color_name,
    size_label,
    selling_price,
    branch_id,
    branch_code,
    branch_name,
    city,
    available_quantity,
    in_transit_quantity,
    stock_status,
    image_path
   FROM clothing_store.v_inventory_catalog
  WHERE (available_quantity <= 3);


ALTER VIEW clothing_store.v_low_stock OWNER TO postgres;

--
-- Name: branch_inventory inventory_id; Type: DEFAULT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.branch_inventory ALTER COLUMN inventory_id SET DEFAULT nextval('clothing_store.branch_inventory_inventory_id_seq'::regclass);


--
-- Name: branches branch_id; Type: DEFAULT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.branches ALTER COLUMN branch_id SET DEFAULT nextval('clothing_store.branches_branch_id_seq'::regclass);


--
-- Name: categories category_id; Type: DEFAULT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.categories ALTER COLUMN category_id SET DEFAULT nextval('clothing_store.categories_category_id_seq'::regclass);


--
-- Name: colors color_id; Type: DEFAULT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.colors ALTER COLUMN color_id SET DEFAULT nextval('clothing_store.colors_color_id_seq'::regclass);


--
-- Name: product_images image_id; Type: DEFAULT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_images ALTER COLUMN image_id SET DEFAULT nextval('clothing_store.product_images_image_id_seq'::regclass);


--
-- Name: product_variants variant_id; Type: DEFAULT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_variants ALTER COLUMN variant_id SET DEFAULT nextval('clothing_store.product_variants_variant_id_seq'::regclass);


--
-- Name: products product_id; Type: DEFAULT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.products ALTER COLUMN product_id SET DEFAULT nextval('clothing_store.products_product_id_seq'::regclass);


--
-- Name: sizes size_id; Type: DEFAULT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.sizes ALTER COLUMN size_id SET DEFAULT nextval('clothing_store.sizes_size_id_seq'::regclass);


--
-- Data for Name: cart_items; Type: TABLE DATA; Schema: agent_runtime; Owner: postgres
--

COPY agent_runtime.cart_items (cart_item_id, cart_id, product_id, variant_id, branch_id, quantity, unit_price, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: carts; Type: TABLE DATA; Schema: agent_runtime; Owner: postgres
--

COPY agent_runtime.carts (cart_id, session_id, status, expires_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: conversation_messages; Type: TABLE DATA; Schema: agent_runtime; Owner: postgres
--

COPY agent_runtime.conversation_messages (message_id, conversation_id, role, content, payload, created_at) FROM stdin;
2081c6ba-d9bd-47b2-88c6-1c987b709de6	25bd5543-c2a5-4333-8fbc-f843afafe4c1	user	hi	{}	2026-08-05 19:03:35.735132+05
55c973be-9ce6-49e3-a915-1f179f9c7255	25bd5543-c2a5-4333-8fbc-f843afafe4c1	assistant	Sure! Tell me what clothing youΓÇÖre looking for, including any size, color, budget, or branch preference.	{"message": "Sure! Tell me what clothing youΓÇÖre looking for, including any size, color, budget, or branch preference.", "products": [], "conversation_id": "25bd5543-c2a5-4333-8fbc-f843afafe4c1", "suggested_replies": [], "display_references": [], "relaxed_constraints": []}	2026-08-05 19:03:35.744407+05
ccda88f6-fd8a-4a4a-8e6c-c367fa835ff8	25bd5543-c2a5-4333-8fbc-f843afafe4c1	user	i want red trouser in 34 size	{}	2026-08-05 19:13:18.108631+05
163c34c6-8347-4dc6-a3bc-2340597dce42	25bd5543-c2a5-4333-8fbc-f843afafe4c1	assistant	Here are trousers in size 34 from our inventory. While we don't have red options currently, I've found these alternatives that match your size requirement:\n\n1. **Executive Pleated Trousers** (North & Loom)  \n   - Navy Blue | Γé╣4,490 | Available at F-7 Store (Islamabad) & Gulberg Flagship (Lahore)  \n   - Tailored fit, formal style  \n\n2. **Studio Drawstring Trousers** (Daily Form)  \n   - Black | Γé╣3,490 | Available at Clifton Store (Karachi)  \n   - Relaxed fit, smart-casual  \n\n3. **Comfort Stretch Trousers** (Daily Form)  \n   - Navy Blue | Γé╣3,790 | Available at Gulberg Flagship (Lahore)  \n   - Stretchy material for all-day comfort  \n\nAll options are in stock and within your budget. Would you like assistance narrowing down based on material, brand, or location?	{"message": "Here are trousers in size 34 from our inventory. While we don't have red options currently, I've found these alternatives that match your size requirement:\\n\\n1. **Executive Pleated Trousers** (North & Loom)  \\n   - Navy Blue | Γé╣4,490 | Available at F-7 Store (Islamabad) & Gulberg Flagship (Lahore)  \\n   - Tailored fit, formal style  \\n\\n2. **Studio Drawstring Trousers** (Daily Form)  \\n   - Black | Γé╣3,490 | Available at Clifton Store (Karachi)  \\n   - Relaxed fit, smart-casual  \\n\\n3. **Comfort Stretch Trousers** (Daily Form)  \\n   - Navy Blue | Γé╣3,790 | Available at Gulberg Flagship (Lahore)  \\n   - Stretchy material for all-day comfort  \\n\\nAll options are in stock and within your budget. Would you like assistance narrowing down based on material, brand, or location?", "products": [{"fit": "Tailored", "sku": "MP-TR-012-NAV-34", "city": "Islamabad", "size": "34", "brand": "North & Loom", "color": "Navy Blue", "price": "4490.00", "score": 63.0, "season": "All Season", "material": "Poly-Viscose", "branch_id": 2, "image_url": "/assets/executive-trousers.svg", "mismatches": ["Different color"], "product_id": 12, "variant_id": 165, "branch_code": "ISB-F7-01", "branch_name": "F-7 Store", "search_tags": ["office", "formal", "professional", "tailored", "business"], "article_code": "MP-TR-012", "product_name": "Executive Pleated Trousers", "category_name": "Trousers", "match_reasons": ["Category match", "Requested size", "Within budget", "In stock"], "available_quantity": 21, "in_transit_quantity": 0}, {"fit": "Relaxed", "sku": "MP-TR-024-BLA-34", "city": "Karachi", "size": "34", "brand": "Daily Form", "color": "Black", "price": "3490.00", "score": 63.0, "season": "All Season", "material": "Cotton Blend", "branch_id": 3, "image_url": "/assets/studio-drawstring-trousers.svg", "mismatches": ["Different color"], "product_id": 24, "variant_id": 339, "branch_code": "KHI-CLF-01", "branch_name": "Clifton Store", "search_tags": ["comfortable", "travel", "smart-casual", "relaxed", "office"], "article_code": "MP-TR-024", "product_name": "Studio Drawstring Trousers", "category_name": "Trousers", "match_reasons": ["Category match", "Requested size", "Within budget", "In stock"], "available_quantity": 20, "in_transit_quantity": 0}, {"fit": "Tailored", "sku": "MP-TR-012-CHA-34", "city": "Karachi", "size": "34", "brand": "North & Loom", "color": "Charcoal", "price": "4490.00", "score": 63.0, "season": "All Season", "material": "Poly-Viscose", "branch_id": 3, "image_url": "/assets/executive-trousers.svg", "mismatches": ["Different color"], "product_id": 12, "variant_id": 170, "branch_code": "KHI-CLF-01", "branch_name": "Clifton Store", "search_tags": ["office", "formal", "professional", "tailored", "business"], "article_code": "MP-TR-012", "product_name": "Executive Pleated Trousers", "category_name": "Trousers", "match_reasons": ["Category match", "Requested size", "Within budget", "In stock"], "available_quantity": 19, "in_transit_quantity": 0}, {"fit": "Relaxed", "sku": "MP-TR-024-GRE-34", "city": "Karachi", "size": "34", "brand": "Daily Form", "color": "Grey", "price": "3490.00", "score": 63.0, "season": "All Season", "material": "Cotton Blend", "branch_id": 3, "image_url": "/assets/studio-drawstring-trousers.svg", "mismatches": ["Different color"], "product_id": 24, "variant_id": 346, "branch_code": "KHI-CLF-01", "branch_name": "Clifton Store", "search_tags": ["comfortable", "travel", "smart-casual", "relaxed", "office"], "article_code": "MP-TR-024", "product_name": "Studio Drawstring Trousers", "category_name": "Trousers", "match_reasons": ["Category match", "Requested size", "Within budget", "In stock"], "available_quantity": 19, "in_transit_quantity": 0}, {"fit": "Regular", "sku": "MP-TR-013-NAV-34", "city": "Lahore", "size": "34", "brand": "Daily Form", "color": "Navy Blue", "price": "3790.00", "score": 63.0, "season": "All Season", "material": "Cotton Stretch Blend", "branch_id": 1, "image_url": "/assets/comfort-stretch-trousers.svg", "mismatches": ["Different color"], "product_id": 13, "variant_id": 180, "branch_code": "LHR-GLB-01", "branch_name": "Gulberg Flagship", "search_tags": ["office", "comfortable", "smart-casual", "stretch", "travel"], "article_code": "MP-TR-013", "product_name": "Comfort Stretch Trousers", "category_name": "Trousers", "match_reasons": ["Category match", "Requested size", "Within budget", "In stock"], "available_quantity": 17, "in_transit_quantity": 0}, {"fit": "Tailored", "sku": "MP-TR-012-NAV-34", "city": "Lahore", "size": "34", "brand": "North & Loom", "color": "Navy Blue", "price": "4490.00", "score": 63.0, "season": "All Season", "material": "Poly-Viscose", "branch_id": 1, "image_url": "/assets/executive-trousers.svg", "mismatches": ["Different color"], "product_id": 12, "variant_id": 165, "branch_code": "LHR-GLB-01", "branch_name": "Gulberg Flagship", "search_tags": ["office", "formal", "professional", "tailored", "business"], "article_code": "MP-TR-012", "product_name": "Executive Pleated Trousers", "category_name": "Trousers", "match_reasons": ["Category match", "Requested size", "Within budget", "In stock"], "available_quantity": 16, "in_transit_quantity": 0}], "conversation_id": "25bd5543-c2a5-4333-8fbc-f843afafe4c1", "suggested_replies": [], "display_references": [], "relaxed_constraints": ["colors"]}	2026-08-05 19:13:18.118959+05
\.


--
-- Data for Name: conversations; Type: TABLE DATA; Schema: agent_runtime; Owner: postgres
--

COPY agent_runtime.conversations (conversation_id, session_id, status, preferences, created_at, updated_at) FROM stdin;
53c73025-c5a0-4ac3-a2e8-ef6574947a7d	d5a5c23c-019c-4216-8925-faa03435db54	ACTIVE	{}	2026-08-05 18:49:39.664033+05	2026-08-05 18:49:39.664038+05
8cede7ed-fc7f-419e-ac02-fecc5eeac508	29b5575e-2249-41f4-a878-520c99c12875	ACTIVE	{}	2026-08-05 18:49:42.853337+05	2026-08-05 18:49:42.853339+05
e3d4edeb-c3f1-497c-ac4f-bb6dfd48800c	4f678e77-d312-4b9f-8d6b-11db76aecd0a	ACTIVE	{}	2026-08-05 18:49:43.05072+05	2026-08-05 18:49:43.050721+05
42c78010-2741-41ce-9650-e2518f29dbee	0a9236a3-d4a8-4aec-bd98-96431e962697	ACTIVE	{}	2026-08-05 18:49:43.263094+05	2026-08-05 18:49:43.263096+05
4ce6a55d-ece6-4fa0-bbf6-16a4072d26ea	e18d04fc-c7b8-4744-970f-541eafbba93e	ACTIVE	{}	2026-08-05 18:49:43.516411+05	2026-08-05 18:49:43.516413+05
4d3ee532-332a-4006-88bc-f4cf30ab630d	55a1f829-01c2-46f0-8c8d-01a0d8e169f6	ACTIVE	{}	2026-08-05 18:49:43.722151+05	2026-08-05 18:49:43.722153+05
911034c2-6efa-4b5e-969c-2012e374e21e	abd12af4-afda-48d3-a93d-c28f77609e4f	ACTIVE	{}	2026-08-05 18:49:43.928566+05	2026-08-05 18:49:43.928567+05
f8b9652c-df30-4e9e-96eb-0fa78f3db99e	191191a4-9339-4b91-81ff-3d7986234b67	ACTIVE	{}	2026-08-05 18:53:08.797161+05	2026-08-05 18:53:08.797171+05
6d93c2d5-a000-41f5-8f0f-a3a559724b72	25fc5d92-7044-487a-92c8-42e88cb0f6cb	ACTIVE	{}	2026-08-05 18:53:08.970632+05	2026-08-05 18:53:08.97064+05
9bc4e0c7-6b9e-46ab-aba1-f44968c56f02	be41ad3f-4a6d-44f0-80f6-c182a1bbeee9	ACTIVE	{}	2026-08-05 18:59:22.560113+05	2026-08-05 18:59:22.56012+05
1e221116-444f-47d6-ab17-7f34a3eb05d1	5061843d-9053-4c9b-ad4b-75fc09488f76	ACTIVE	{}	2026-08-05 18:59:22.561474+05	2026-08-05 18:59:22.561477+05
891ff661-226b-463c-adea-62b6b51e77e8	04d94d77-d11c-4617-9a6a-df6c79fc3b20	ACTIVE	{}	2026-08-05 19:03:17.119218+05	2026-08-05 19:03:17.119222+05
25bd5543-c2a5-4333-8fbc-f843afafe4c1	4a1b3fb8-2d6c-4a11-a732-4b0a15570a9e	ACTIVE	{"sizes": ["34"], "colors": ["red"], "category": "trousers", "query_text": "red trouser", "in_stock_only": true, "semantic_tags": ["trouser"]}	2026-08-05 19:03:17.120078+05	2026-08-06 00:13:18.115248+05
\.


--
-- Data for Name: displayed_results; Type: TABLE DATA; Schema: agent_runtime; Owner: postgres
--

COPY agent_runtime.displayed_results (displayed_result_id, conversation_id, message_id, "position", product_id, variant_id, branch_id, created_at) FROM stdin;
9e507001-35ad-4e66-91de-6493fe8bb362	25bd5543-c2a5-4333-8fbc-f843afafe4c1	163c34c6-8347-4dc6-a3bc-2340597dce42	1	12	165	2	2026-08-05 19:13:18.130925+05
21940714-86d3-4c76-9c2d-3332d2fe45d1	25bd5543-c2a5-4333-8fbc-f843afafe4c1	163c34c6-8347-4dc6-a3bc-2340597dce42	2	24	339	3	2026-08-05 19:13:18.130944+05
57eaf7b4-dbf7-4522-a85d-92541cfa20b6	25bd5543-c2a5-4333-8fbc-f843afafe4c1	163c34c6-8347-4dc6-a3bc-2340597dce42	3	12	170	3	2026-08-05 19:13:18.130955+05
9bf43c47-e9c7-4904-843e-5721cb5595f3	25bd5543-c2a5-4333-8fbc-f843afafe4c1	163c34c6-8347-4dc6-a3bc-2340597dce42	4	24	346	3	2026-08-05 19:13:18.130968+05
e8d899d3-7ac8-415e-8a0d-05da4dd90ce1	25bd5543-c2a5-4333-8fbc-f843afafe4c1	163c34c6-8347-4dc6-a3bc-2340597dce42	5	13	180	1	2026-08-05 19:13:18.130978+05
b9798915-f170-4a09-b22b-61a2869a0603	25bd5543-c2a5-4333-8fbc-f843afafe4c1	163c34c6-8347-4dc6-a3bc-2340597dce42	6	12	165	1	2026-08-05 19:13:18.130987+05
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: agent_runtime; Owner: postgres
--

COPY agent_runtime.order_items (order_item_id, order_id, product_id, variant_id, branch_id, quantity, unit_price) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: agent_runtime; Owner: postgres
--

COPY agent_runtime.orders (order_id, session_id, cart_id, status, subtotal, confirmation_expires_at, created_at, confirmed_at) FROM stdin;
\.


--
-- Data for Name: stock_reservations; Type: TABLE DATA; Schema: agent_runtime; Owner: postgres
--

COPY agent_runtime.stock_reservations (reservation_id, order_id, variant_id, branch_id, quantity, status, expires_at) FROM stdin;
\.


--
-- Data for Name: branch_inventory; Type: TABLE DATA; Schema: clothing_store; Owner: postgres
--

COPY clothing_store.branch_inventory (inventory_id, branch_id, variant_id, quantity_on_hand, reserved_quantity, damaged_quantity, in_transit_quantity, reorder_level, updated_at) FROM stdin;
1	1	2	11	0	0	0	4	2026-08-05 23:30:54.931579+05
2	1	3	14	0	0	0	4	2026-08-05 23:30:54.931579+05
3	1	4	17	0	0	0	4	2026-08-05 23:30:54.931579+05
4	1	5	20	0	0	0	4	2026-08-05 23:30:54.931579+05
5	1	7	4	0	0	0	4	2026-08-05 23:30:54.931579+05
6	1	8	7	0	0	0	4	2026-08-05 23:30:54.931579+05
7	1	9	10	0	0	0	4	2026-08-05 23:30:54.931579+05
8	1	10	13	1	0	0	4	2026-08-05 23:30:54.931579+05
9	1	11	16	0	0	0	4	2026-08-05 23:30:54.931579+05
10	1	12	19	0	0	0	4	2026-08-05 23:30:54.931579+05
11	1	14	3	0	0	0	3	2026-08-05 23:30:54.931579+05
12	1	15	6	0	0	0	3	2026-08-05 23:30:54.931579+05
13	1	16	9	0	0	0	3	2026-08-05 23:30:54.931579+05
14	1	17	12	0	0	0	3	2026-08-05 23:30:54.931579+05
15	1	19	18	0	0	0	3	2026-08-05 23:30:54.931579+05
16	1	20	21	0	0	0	3	2026-08-05 23:30:54.931579+05
17	1	21	2	0	0	0	3	2026-08-05 23:30:54.931579+05
18	1	22	5	0	0	0	3	2026-08-05 23:30:54.931579+05
19	1	24	11	0	0	0	4	2026-08-05 23:30:54.931579+05
20	1	25	14	0	0	0	4	2026-08-05 23:30:54.931579+05
21	1	26	17	0	0	0	4	2026-08-05 23:30:54.931579+05
22	1	27	20	0	0	0	4	2026-08-05 23:30:54.931579+05
23	1	28	1	0	0	0	4	2026-08-05 23:30:54.931579+05
24	1	29	4	0	0	0	4	2026-08-05 23:30:54.931579+05
25	1	31	10	0	0	0	4	2026-08-05 23:30:54.931579+05
26	1	32	13	1	0	0	4	2026-08-05 23:30:54.931579+05
27	1	33	0	0	0	0	4	2026-08-05 23:30:54.931579+05
28	1	34	19	0	0	0	4	2026-08-05 23:30:54.931579+05
29	1	36	3	0	0	0	4	2026-08-05 23:30:54.931579+05
30	1	37	6	0	0	0	4	2026-08-05 23:30:54.931579+05
31	1	38	9	0	0	0	4	2026-08-05 23:30:54.931579+05
32	1	39	12	0	0	0	4	2026-08-05 23:30:54.931579+05
33	1	41	18	0	0	0	4	2026-08-05 23:30:54.931579+05
34	1	42	21	0	1	0	4	2026-08-05 23:30:54.931579+05
35	1	43	2	0	0	0	4	2026-08-05 23:30:54.931579+05
36	1	44	5	0	0	0	4	2026-08-05 23:30:54.931579+05
37	1	45	8	0	0	0	4	2026-08-05 23:30:54.931579+05
38	1	46	11	0	0	0	4	2026-08-05 23:30:54.931579+05
39	1	48	17	0	0	0	4	2026-08-05 23:30:54.931579+05
40	1	49	20	0	0	0	4	2026-08-05 23:30:54.931579+05
41	1	50	1	0	0	0	4	2026-08-05 23:30:54.931579+05
42	1	51	4	0	0	0	4	2026-08-05 23:30:54.931579+05
43	1	53	10	0	0	0	4	2026-08-05 23:30:54.931579+05
44	1	54	13	1	0	0	4	2026-08-05 23:30:54.931579+05
45	1	55	16	0	0	0	4	2026-08-05 23:30:54.931579+05
46	1	56	19	0	0	0	4	2026-08-05 23:30:54.931579+05
47	1	58	3	0	0	0	4	2026-08-05 23:30:54.931579+05
48	1	59	6	0	0	0	4	2026-08-05 23:30:54.931579+05
49	1	60	9	0	0	0	4	2026-08-05 23:30:54.931579+05
50	1	61	12	0	0	0	4	2026-08-05 23:30:54.931579+05
51	1	62	15	0	0	0	4	2026-08-05 23:30:54.931579+05
52	1	63	18	0	0	0	4	2026-08-05 23:30:54.931579+05
53	1	65	2	0	0	0	4	2026-08-05 23:30:54.931579+05
54	1	66	5	0	0	0	4	2026-08-05 23:30:54.931579+05
55	1	67	8	0	0	0	4	2026-08-05 23:30:54.931579+05
56	1	68	11	0	0	0	4	2026-08-05 23:30:54.931579+05
57	1	70	0	0	0	0	4	2026-08-05 23:30:54.931579+05
58	1	71	20	0	0	0	4	2026-08-05 23:30:54.931579+05
59	1	72	1	0	0	0	4	2026-08-05 23:30:54.931579+05
60	1	73	4	0	0	0	4	2026-08-05 23:30:54.931579+05
61	1	75	10	0	0	0	4	2026-08-05 23:30:54.931579+05
62	1	76	13	1	0	0	4	2026-08-05 23:30:54.931579+05
63	1	77	16	0	0	0	4	2026-08-05 23:30:54.931579+05
64	1	78	19	0	0	0	4	2026-08-05 23:30:54.931579+05
65	1	79	0	0	0	0	4	2026-08-05 23:30:54.931579+05
66	1	80	3	0	0	0	4	2026-08-05 23:30:54.931579+05
67	1	82	9	0	0	0	4	2026-08-05 23:30:54.931579+05
68	1	83	12	0	0	0	4	2026-08-05 23:30:54.931579+05
69	1	84	15	0	0	0	4	2026-08-05 23:30:54.931579+05
70	1	85	18	0	1	0	4	2026-08-05 23:30:54.931579+05
71	1	87	2	0	0	0	4	2026-08-05 23:30:54.931579+05
72	1	88	5	0	0	0	4	2026-08-05 23:30:54.931579+05
73	1	89	8	0	0	0	4	2026-08-05 23:30:54.931579+05
74	1	90	11	0	0	0	4	2026-08-05 23:30:54.931579+05
75	1	92	17	0	0	0	4	2026-08-05 23:30:54.931579+05
76	1	93	20	0	0	0	4	2026-08-05 23:30:54.931579+05
77	1	94	1	0	0	0	4	2026-08-05 23:30:54.931579+05
78	1	95	4	0	0	0	4	2026-08-05 23:30:54.931579+05
79	1	96	7	0	0	0	4	2026-08-05 23:30:54.931579+05
80	1	97	10	0	0	0	4	2026-08-05 23:30:54.931579+05
81	1	99	16	0	0	0	3	2026-08-05 23:30:54.931579+05
82	1	100	19	0	0	0	3	2026-08-05 23:30:54.931579+05
83	1	101	0	0	0	4	3	2026-08-05 23:30:54.931579+05
84	1	102	3	0	0	0	3	2026-08-05 23:30:54.931579+05
85	1	104	9	0	0	0	3	2026-08-05 23:30:54.931579+05
86	1	105	12	0	0	0	3	2026-08-05 23:30:54.931579+05
87	1	106	15	0	0	0	3	2026-08-05 23:30:54.931579+05
88	1	107	0	0	0	4	3	2026-08-05 23:30:54.931579+05
89	1	109	2	0	0	0	4	2026-08-05 23:30:54.931579+05
90	1	110	5	0	0	0	4	2026-08-05 23:30:54.931579+05
91	1	111	8	0	0	0	4	2026-08-05 23:30:54.931579+05
92	1	112	11	0	0	0	4	2026-08-05 23:30:54.931579+05
93	1	113	14	0	0	0	4	2026-08-05 23:30:54.931579+05
94	1	114	17	0	0	0	4	2026-08-05 23:30:54.931579+05
95	1	116	1	0	0	0	4	2026-08-05 23:30:54.931579+05
96	1	117	4	0	0	0	4	2026-08-05 23:30:54.931579+05
97	1	118	7	0	0	0	4	2026-08-05 23:30:54.931579+05
98	1	119	10	0	0	0	4	2026-08-05 23:30:54.931579+05
99	1	121	16	0	0	0	3	2026-08-05 23:30:54.931579+05
100	1	122	19	0	0	0	3	2026-08-05 23:30:54.931579+05
101	1	123	0	0	0	0	3	2026-08-05 23:30:54.931579+05
102	1	124	3	0	0	0	3	2026-08-05 23:30:54.931579+05
103	1	126	9	0	0	0	3	2026-08-05 23:30:54.931579+05
104	1	127	0	0	0	0	3	2026-08-05 23:30:54.931579+05
105	1	128	15	0	1	0	3	2026-08-05 23:30:54.931579+05
106	1	129	18	0	0	0	3	2026-08-05 23:30:54.931579+05
107	1	130	21	0	0	0	3	2026-08-05 23:30:54.931579+05
108	1	131	2	0	0	0	3	2026-08-05 23:30:54.931579+05
109	1	133	8	0	0	0	3	2026-08-05 23:30:54.931579+05
110	1	134	11	0	0	0	3	2026-08-05 23:30:54.931579+05
111	1	135	14	0	0	0	3	2026-08-05 23:30:54.931579+05
112	1	136	17	0	0	0	3	2026-08-05 23:30:54.931579+05
113	1	138	1	0	0	0	3	2026-08-05 23:30:54.931579+05
114	1	139	4	0	0	0	3	2026-08-05 23:30:54.931579+05
115	1	140	7	0	0	0	3	2026-08-05 23:30:54.931579+05
116	1	141	10	0	0	0	3	2026-08-05 23:30:54.931579+05
117	1	143	16	0	0	0	3	2026-08-05 23:30:54.931579+05
118	1	144	0	0	0	0	3	2026-08-05 23:30:54.931579+05
119	1	145	0	0	0	0	3	2026-08-05 23:30:54.931579+05
120	1	146	3	0	0	0	3	2026-08-05 23:30:54.931579+05
121	1	147	6	0	0	0	3	2026-08-05 23:30:54.931579+05
122	1	148	9	0	0	0	3	2026-08-05 23:30:54.931579+05
123	1	150	15	0	0	0	3	2026-08-05 23:30:54.931579+05
124	1	151	18	0	0	0	3	2026-08-05 23:30:54.931579+05
125	1	152	21	0	0	0	3	2026-08-05 23:30:54.931579+05
126	1	153	2	0	0	3	3	2026-08-05 23:30:54.931579+05
127	1	155	8	0	0	0	3	2026-08-05 23:30:54.931579+05
128	1	156	11	0	0	0	3	2026-08-05 23:30:54.931579+05
129	1	157	14	0	0	0	3	2026-08-05 23:30:54.931579+05
130	1	158	17	0	0	0	3	2026-08-05 23:30:54.931579+05
131	1	160	0	0	0	4	3	2026-08-05 23:30:54.931579+05
132	1	161	4	0	0	0	3	2026-08-05 23:30:54.931579+05
133	1	162	7	0	0	0	3	2026-08-05 23:30:54.931579+05
134	1	163	10	0	0	0	3	2026-08-05 23:30:54.931579+05
135	1	164	13	1	0	0	3	2026-08-05 23:30:54.931579+05
136	1	165	16	0	0	0	3	2026-08-05 23:30:54.931579+05
137	1	167	0	0	0	4	3	2026-08-05 23:30:54.931579+05
138	1	168	3	0	0	0	3	2026-08-05 23:30:54.931579+05
139	1	169	6	0	0	0	3	2026-08-05 23:30:54.931579+05
140	1	170	6	0	0	0	3	2026-08-05 23:30:54.931579+05
141	1	172	15	0	0	0	3	2026-08-05 23:30:54.931579+05
142	1	173	18	0	0	0	3	2026-08-05 23:30:54.931579+05
143	1	174	21	0	0	0	3	2026-08-05 23:30:54.931579+05
144	1	175	2	0	0	0	3	2026-08-05 23:30:54.931579+05
145	1	177	8	0	0	0	3	2026-08-05 23:30:54.931579+05
146	1	178	11	0	0	0	3	2026-08-05 23:30:54.931579+05
147	1	179	14	0	0	0	3	2026-08-05 23:30:54.931579+05
148	1	180	17	0	0	0	3	2026-08-05 23:30:54.931579+05
149	1	181	0	0	0	3	3	2026-08-05 23:30:54.931579+05
150	1	182	1	0	0	0	3	2026-08-05 23:30:54.931579+05
151	1	184	7	0	0	0	3	2026-08-05 23:30:54.931579+05
152	1	185	10	0	0	0	3	2026-08-05 23:30:54.931579+05
153	1	186	13	1	0	0	3	2026-08-05 23:30:54.931579+05
154	1	187	16	0	0	0	3	2026-08-05 23:30:54.931579+05
155	1	189	0	0	0	0	3	2026-08-05 23:30:54.931579+05
156	1	190	3	0	0	0	3	2026-08-05 23:30:54.931579+05
157	1	191	6	0	0	0	3	2026-08-05 23:30:54.931579+05
158	1	192	9	0	0	0	3	2026-08-05 23:30:54.931579+05
159	1	194	15	0	0	0	3	2026-08-05 23:30:54.931579+05
160	1	195	18	0	0	0	3	2026-08-05 23:30:54.931579+05
161	1	196	21	0	0	0	3	2026-08-05 23:30:54.931579+05
162	1	197	2	0	0	0	3	2026-08-05 23:30:54.931579+05
163	1	198	5	0	0	0	3	2026-08-05 23:30:54.931579+05
164	1	199	8	0	0	0	3	2026-08-05 23:30:54.931579+05
165	1	201	14	0	0	0	3	2026-08-05 23:30:54.931579+05
166	1	202	17	0	0	0	3	2026-08-05 23:30:54.931579+05
167	1	203	20	0	0	0	3	2026-08-05 23:30:54.931579+05
168	1	204	1	0	0	0	3	2026-08-05 23:30:54.931579+05
169	1	206	7	0	0	0	4	2026-08-05 23:30:54.931579+05
170	1	207	10	0	0	0	4	2026-08-05 23:30:54.931579+05
171	1	208	13	1	0	0	4	2026-08-05 23:30:54.931579+05
172	1	209	16	0	0	0	4	2026-08-05 23:30:54.931579+05
173	1	211	0	0	0	0	4	2026-08-05 23:30:54.931579+05
174	1	212	3	0	0	0	4	2026-08-05 23:30:54.931579+05
175	1	213	6	0	0	0	4	2026-08-05 23:30:54.931579+05
176	1	214	9	0	1	0	4	2026-08-05 23:30:54.931579+05
177	1	215	12	0	0	0	3	2026-08-05 23:30:54.931579+05
178	1	216	15	0	0	0	3	2026-08-05 23:30:54.931579+05
179	1	218	0	0	0	4	3	2026-08-05 23:30:54.931579+05
180	1	219	2	0	0	0	3	2026-08-05 23:30:54.931579+05
181	1	220	5	0	0	0	3	2026-08-05 23:30:54.931579+05
182	1	221	8	0	0	0	3	2026-08-05 23:30:54.931579+05
183	1	223	14	0	0	0	3	2026-08-05 23:30:54.931579+05
184	1	224	17	0	0	0	3	2026-08-05 23:30:54.931579+05
185	1	225	20	0	0	0	3	2026-08-05 23:30:54.931579+05
186	1	226	1	0	0	0	3	2026-08-05 23:30:54.931579+05
187	1	228	7	0	0	0	3	2026-08-05 23:30:54.931579+05
188	1	229	10	0	0	0	3	2026-08-05 23:30:54.931579+05
189	1	230	13	1	0	0	3	2026-08-05 23:30:54.931579+05
190	1	231	16	0	0	0	3	2026-08-05 23:30:54.931579+05
191	1	232	19	0	0	0	3	2026-08-05 23:30:54.931579+05
192	1	233	0	0	0	4	3	2026-08-05 23:30:54.931579+05
193	1	235	6	0	0	0	4	2026-08-05 23:30:54.931579+05
194	1	236	9	0	0	0	4	2026-08-05 23:30:54.931579+05
195	1	237	12	0	0	0	4	2026-08-05 23:30:54.931579+05
196	1	238	15	0	0	0	4	2026-08-05 23:30:54.931579+05
197	1	240	21	0	0	0	4	2026-08-05 23:30:54.931579+05
198	1	241	2	0	0	0	4	2026-08-05 23:30:54.931579+05
199	1	242	5	0	0	0	4	2026-08-05 23:30:54.931579+05
200	1	243	8	0	0	0	4	2026-08-05 23:30:54.931579+05
201	1	245	14	0	0	0	4	2026-08-05 23:30:54.931579+05
202	1	246	17	0	0	0	4	2026-08-05 23:30:54.931579+05
203	1	247	20	0	0	0	4	2026-08-05 23:30:54.931579+05
204	1	248	1	0	0	0	4	2026-08-05 23:30:54.931579+05
205	1	249	4	0	0	0	4	2026-08-05 23:30:54.931579+05
206	1	250	7	0	0	0	4	2026-08-05 23:30:54.931579+05
207	1	252	13	1	0	0	4	2026-08-05 23:30:54.931579+05
208	1	253	16	0	0	0	4	2026-08-05 23:30:54.931579+05
209	1	254	19	0	0	0	4	2026-08-05 23:30:54.931579+05
210	1	255	0	0	0	0	4	2026-08-05 23:30:54.931579+05
211	1	257	6	0	1	0	4	2026-08-05 23:30:54.931579+05
212	1	258	9	0	0	0	4	2026-08-05 23:30:54.931579+05
213	1	259	12	0	0	0	4	2026-08-05 23:30:54.931579+05
214	1	260	15	0	0	0	4	2026-08-05 23:30:54.931579+05
215	1	262	21	0	0	0	4	2026-08-05 23:30:54.931579+05
216	1	263	2	0	0	0	4	2026-08-05 23:30:54.931579+05
217	1	264	5	0	0	0	4	2026-08-05 23:30:54.931579+05
218	1	265	8	0	0	0	3	2026-08-05 23:30:54.931579+05
219	1	266	11	0	0	0	3	2026-08-05 23:30:54.931579+05
220	1	267	14	0	0	0	3	2026-08-05 23:30:54.931579+05
221	1	269	20	0	0	0	3	2026-08-05 23:30:54.931579+05
222	1	270	1	0	0	0	3	2026-08-05 23:30:54.931579+05
223	1	271	4	0	0	0	3	2026-08-05 23:30:54.931579+05
224	1	272	7	0	0	0	3	2026-08-05 23:30:54.931579+05
225	1	274	13	1	0	0	3	2026-08-05 23:30:54.931579+05
226	1	275	16	0	0	0	3	2026-08-05 23:30:54.931579+05
227	1	276	19	0	0	0	3	2026-08-05 23:30:54.931579+05
228	1	277	0	0	0	0	3	2026-08-05 23:30:54.931579+05
229	1	279	6	0	0	0	3	2026-08-05 23:30:54.931579+05
230	1	280	9	0	0	0	3	2026-08-05 23:30:54.931579+05
231	1	281	12	0	0	0	3	2026-08-05 23:30:54.931579+05
232	1	282	15	0	0	0	3	2026-08-05 23:30:54.931579+05
233	1	297	16	0	0	0	4	2026-08-05 23:30:54.931579+05
234	1	298	19	0	0	0	4	2026-08-05 23:30:54.931579+05
235	1	299	0	0	0	4	4	2026-08-05 23:30:54.931579+05
236	1	300	3	0	0	0	4	2026-08-05 23:30:54.931579+05
237	1	301	6	0	0	0	4	2026-08-05 23:30:54.931579+05
238	1	303	12	0	0	0	4	2026-08-05 23:30:54.931579+05
239	1	304	15	0	0	0	4	2026-08-05 23:30:54.931579+05
240	1	305	18	0	0	0	4	2026-08-05 23:30:54.931579+05
241	1	306	21	0	0	0	4	2026-08-05 23:30:54.931579+05
242	1	308	5	0	0	0	4	2026-08-05 23:30:54.931579+05
243	1	309	8	0	0	0	4	2026-08-05 23:30:54.931579+05
244	1	310	11	0	0	0	4	2026-08-05 23:30:54.931579+05
245	1	311	14	0	0	0	4	2026-08-05 23:30:54.931579+05
246	1	313	20	0	0	0	4	2026-08-05 23:30:54.931579+05
247	1	314	1	0	0	3	4	2026-08-05 23:30:54.931579+05
248	1	315	4	0	0	0	4	2026-08-05 23:30:54.931579+05
249	1	316	7	0	0	0	4	2026-08-05 23:30:54.931579+05
250	1	317	10	0	0	0	4	2026-08-05 23:30:54.931579+05
251	1	318	13	1	0	0	4	2026-08-05 23:30:54.931579+05
252	1	320	19	0	0	0	4	2026-08-05 23:30:54.931579+05
253	1	321	0	0	0	3	4	2026-08-05 23:30:54.931579+05
254	1	322	3	0	0	0	4	2026-08-05 23:30:54.931579+05
255	1	323	6	0	0	0	4	2026-08-05 23:30:54.931579+05
256	1	325	12	0	0	0	4	2026-08-05 23:30:54.931579+05
257	1	326	15	0	0	0	4	2026-08-05 23:30:54.931579+05
258	1	327	18	0	0	0	4	2026-08-05 23:30:54.931579+05
259	1	328	21	0	0	0	4	2026-08-05 23:30:54.931579+05
260	1	330	5	0	0	0	4	2026-08-05 23:30:54.931579+05
261	1	331	8	0	0	0	4	2026-08-05 23:30:54.931579+05
262	1	332	11	0	0	0	4	2026-08-05 23:30:54.931579+05
263	1	333	14	0	0	0	4	2026-08-05 23:30:54.931579+05
264	1	334	17	0	0	0	4	2026-08-05 23:30:54.931579+05
265	1	335	20	0	0	0	4	2026-08-05 23:30:54.931579+05
266	2	1	13	0	0	0	4	2026-08-05 23:30:54.931579+05
267	2	3	19	0	0	0	4	2026-08-05 23:30:54.931579+05
268	2	4	0	0	0	4	4	2026-08-05 23:30:54.931579+05
269	2	5	3	0	0	0	4	2026-08-05 23:30:54.931579+05
270	2	6	6	0	0	0	4	2026-08-05 23:30:54.931579+05
271	2	7	9	0	0	0	4	2026-08-05 23:30:54.931579+05
272	2	8	12	0	0	0	4	2026-08-05 23:30:54.931579+05
273	2	10	18	0	0	0	4	2026-08-05 23:30:54.931579+05
274	2	11	21	0	0	0	4	2026-08-05 23:30:54.931579+05
275	2	12	2	0	0	3	4	2026-08-05 23:30:54.931579+05
276	2	13	5	0	0	0	3	2026-08-05 23:30:54.931579+05
277	2	15	11	0	0	0	3	2026-08-05 23:30:54.931579+05
278	2	16	14	0	0	0	3	2026-08-05 23:30:54.931579+05
279	2	17	17	0	0	0	3	2026-08-05 23:30:54.931579+05
280	2	18	20	0	0	0	3	2026-08-05 23:30:54.931579+05
281	2	20	4	1	0	0	3	2026-08-05 23:30:54.931579+05
282	2	21	7	0	0	0	3	2026-08-05 23:30:54.931579+05
283	2	22	10	0	0	0	3	2026-08-05 23:30:54.931579+05
284	2	23	13	0	0	0	4	2026-08-05 23:30:54.931579+05
285	2	24	16	0	0	0	4	2026-08-05 23:30:54.931579+05
286	2	25	19	0	0	0	4	2026-08-05 23:30:54.931579+05
287	2	27	3	0	0	0	4	2026-08-05 23:30:54.931579+05
288	2	28	6	0	0	0	4	2026-08-05 23:30:54.931579+05
289	2	29	0	0	0	0	4	2026-08-05 23:30:54.931579+05
290	2	30	12	0	0	0	4	2026-08-05 23:30:54.931579+05
291	2	32	18	0	0	0	4	2026-08-05 23:30:54.931579+05
292	2	33	21	0	0	0	4	2026-08-05 23:30:54.931579+05
293	2	34	2	0	0	0	4	2026-08-05 23:30:54.931579+05
294	2	35	5	0	0	0	4	2026-08-05 23:30:54.931579+05
295	2	37	11	0	0	0	4	2026-08-05 23:30:54.931579+05
296	2	38	14	0	0	0	4	2026-08-05 23:30:54.931579+05
297	2	39	17	0	0	0	4	2026-08-05 23:30:54.931579+05
298	2	40	20	0	0	0	4	2026-08-05 23:30:54.931579+05
299	2	41	1	0	0	0	4	2026-08-05 23:30:54.931579+05
300	2	42	4	1	0	0	4	2026-08-05 23:30:54.931579+05
301	2	44	10	0	0	0	4	2026-08-05 23:30:54.931579+05
302	2	45	13	0	0	0	4	2026-08-05 23:30:54.931579+05
303	2	46	16	0	0	0	4	2026-08-05 23:30:54.931579+05
304	2	47	19	0	0	0	4	2026-08-05 23:30:54.931579+05
305	2	49	3	0	0	0	4	2026-08-05 23:30:54.931579+05
306	2	50	6	0	0	0	4	2026-08-05 23:30:54.931579+05
307	2	51	9	0	0	0	4	2026-08-05 23:30:54.931579+05
308	2	52	12	0	0	0	4	2026-08-05 23:30:54.931579+05
309	2	54	18	0	0	0	4	2026-08-05 23:30:54.931579+05
310	2	55	21	0	0	0	4	2026-08-05 23:30:54.931579+05
311	2	56	2	0	0	0	4	2026-08-05 23:30:54.931579+05
312	2	57	5	0	0	0	4	2026-08-05 23:30:54.931579+05
313	2	58	8	0	0	0	4	2026-08-05 23:30:54.931579+05
314	2	59	11	0	0	0	4	2026-08-05 23:30:54.931579+05
315	2	61	17	0	0	0	4	2026-08-05 23:30:54.931579+05
316	2	62	20	0	0	0	4	2026-08-05 23:30:54.931579+05
317	2	63	1	0	0	0	4	2026-08-05 23:30:54.931579+05
318	2	64	4	1	0	0	4	2026-08-05 23:30:54.931579+05
319	2	66	0	0	0	0	4	2026-08-05 23:30:54.931579+05
320	2	67	13	0	0	0	4	2026-08-05 23:30:54.931579+05
321	2	68	16	0	0	0	4	2026-08-05 23:30:54.931579+05
322	2	69	19	0	0	0	4	2026-08-05 23:30:54.931579+05
323	2	71	3	0	0	0	4	2026-08-05 23:30:54.931579+05
324	2	72	6	0	0	0	4	2026-08-05 23:30:54.931579+05
325	2	73	9	0	0	0	4	2026-08-05 23:30:54.931579+05
326	2	74	12	0	0	0	4	2026-08-05 23:30:54.931579+05
327	2	75	15	1	0	0	4	2026-08-05 23:30:54.931579+05
328	2	76	18	0	0	0	4	2026-08-05 23:30:54.931579+05
329	2	78	2	0	0	0	4	2026-08-05 23:30:54.931579+05
330	2	79	5	0	0	0	4	2026-08-05 23:30:54.931579+05
331	2	80	8	0	0	0	4	2026-08-05 23:30:54.931579+05
332	2	81	11	0	0	0	4	2026-08-05 23:30:54.931579+05
333	2	83	17	0	0	0	4	2026-08-05 23:30:54.931579+05
334	2	84	20	0	1	0	4	2026-08-05 23:30:54.931579+05
335	2	85	1	0	0	0	4	2026-08-05 23:30:54.931579+05
336	2	86	4	1	0	0	4	2026-08-05 23:30:54.931579+05
337	2	88	10	0	0	0	4	2026-08-05 23:30:54.931579+05
338	2	89	13	0	0	0	4	2026-08-05 23:30:54.931579+05
339	2	90	16	0	0	0	4	2026-08-05 23:30:54.931579+05
340	2	91	19	0	0	0	4	2026-08-05 23:30:54.931579+05
341	2	92	0	0	0	0	4	2026-08-05 23:30:54.931579+05
342	2	93	3	0	0	0	4	2026-08-05 23:30:54.931579+05
343	2	95	9	0	0	0	4	2026-08-05 23:30:54.931579+05
344	2	96	12	0	0	0	4	2026-08-05 23:30:54.931579+05
345	2	97	15	1	0	0	4	2026-08-05 23:30:54.931579+05
346	2	98	18	0	0	0	3	2026-08-05 23:30:54.931579+05
347	2	100	2	0	0	0	3	2026-08-05 23:30:54.931579+05
348	2	101	5	0	0	0	3	2026-08-05 23:30:54.931579+05
349	2	102	8	0	0	0	3	2026-08-05 23:30:54.931579+05
350	2	103	0	0	0	4	3	2026-08-05 23:30:54.931579+05
351	2	105	17	0	0	0	3	2026-08-05 23:30:54.931579+05
352	2	106	20	0	0	0	3	2026-08-05 23:30:54.931579+05
353	2	107	1	0	0	0	3	2026-08-05 23:30:54.931579+05
354	2	108	4	1	0	0	3	2026-08-05 23:30:54.931579+05
355	2	109	7	0	0	0	4	2026-08-05 23:30:54.931579+05
356	2	110	10	0	0	0	4	2026-08-05 23:30:54.931579+05
357	2	112	16	0	0	0	4	2026-08-05 23:30:54.931579+05
358	2	113	19	0	0	0	4	2026-08-05 23:30:54.931579+05
359	2	114	0	0	0	0	4	2026-08-05 23:30:54.931579+05
360	2	115	3	0	0	0	4	2026-08-05 23:30:54.931579+05
361	2	117	9	0	0	0	4	2026-08-05 23:30:54.931579+05
362	2	118	12	0	0	0	4	2026-08-05 23:30:54.931579+05
363	2	119	15	1	0	0	4	2026-08-05 23:30:54.931579+05
364	2	120	18	0	0	0	4	2026-08-05 23:30:54.931579+05
365	2	122	2	0	0	0	3	2026-08-05 23:30:54.931579+05
366	2	123	5	0	0	0	3	2026-08-05 23:30:54.931579+05
367	2	124	8	0	0	0	3	2026-08-05 23:30:54.931579+05
368	2	125	11	0	0	0	3	2026-08-05 23:30:54.931579+05
369	2	126	14	0	0	0	3	2026-08-05 23:30:54.931579+05
370	2	127	17	0	1	0	3	2026-08-05 23:30:54.931579+05
371	2	129	1	0	0	0	3	2026-08-05 23:30:54.931579+05
372	2	130	4	1	0	0	3	2026-08-05 23:30:54.931579+05
373	2	131	7	0	0	0	3	2026-08-05 23:30:54.931579+05
374	2	132	10	0	0	0	3	2026-08-05 23:30:54.931579+05
375	2	134	16	0	0	0	3	2026-08-05 23:30:54.931579+05
376	2	135	19	0	0	0	3	2026-08-05 23:30:54.931579+05
377	2	136	0	0	0	4	3	2026-08-05 23:30:54.931579+05
378	2	137	3	0	0	0	3	2026-08-05 23:30:54.931579+05
379	2	139	9	0	0	0	3	2026-08-05 23:30:54.931579+05
380	2	140	0	0	0	0	3	2026-08-05 23:30:54.931579+05
381	2	141	15	1	0	0	3	2026-08-05 23:30:54.931579+05
382	2	142	18	0	0	0	3	2026-08-05 23:30:54.931579+05
383	2	143	21	0	0	0	3	2026-08-05 23:30:54.931579+05
384	2	144	2	0	0	0	3	2026-08-05 23:30:54.931579+05
385	2	146	8	0	0	0	3	2026-08-05 23:30:54.931579+05
386	2	147	11	0	0	0	3	2026-08-05 23:30:54.931579+05
387	2	148	14	0	0	0	3	2026-08-05 23:30:54.931579+05
388	2	149	17	0	0	0	3	2026-08-05 23:30:54.931579+05
389	2	151	1	0	0	0	3	2026-08-05 23:30:54.931579+05
390	2	152	4	1	0	0	3	2026-08-05 23:30:54.931579+05
391	2	153	7	0	0	0	3	2026-08-05 23:30:54.931579+05
392	2	154	10	0	0	0	3	2026-08-05 23:30:54.931579+05
393	2	156	16	0	0	0	3	2026-08-05 23:30:54.931579+05
394	2	157	19	0	0	0	3	2026-08-05 23:30:54.931579+05
395	2	158	0	0	0	0	3	2026-08-05 23:30:54.931579+05
396	2	159	3	0	0	0	3	2026-08-05 23:30:54.931579+05
397	2	160	6	0	0	0	3	2026-08-05 23:30:54.931579+05
398	2	161	9	0	0	0	3	2026-08-05 23:30:54.931579+05
399	2	163	15	1	0	0	3	2026-08-05 23:30:54.931579+05
400	2	164	18	0	0	0	3	2026-08-05 23:30:54.931579+05
401	2	165	21	0	0	0	3	2026-08-05 23:30:54.931579+05
402	2	166	2	0	0	3	3	2026-08-05 23:30:54.931579+05
403	2	168	8	0	0	0	3	2026-08-05 23:30:54.931579+05
404	2	169	11	0	0	0	3	2026-08-05 23:30:54.931579+05
405	2	170	14	0	1	0	3	2026-08-05 23:30:54.931579+05
406	2	171	17	0	0	0	3	2026-08-05 23:30:54.931579+05
407	2	173	1	0	0	3	3	2026-08-05 23:30:54.931579+05
408	2	174	4	1	0	0	3	2026-08-05 23:30:54.931579+05
409	2	175	7	0	0	0	3	2026-08-05 23:30:54.931579+05
410	2	176	10	0	0	0	3	2026-08-05 23:30:54.931579+05
411	2	177	0	0	0	0	3	2026-08-05 23:30:54.931579+05
412	2	178	16	0	0	0	3	2026-08-05 23:30:54.931579+05
413	2	180	0	0	0	3	3	2026-08-05 23:30:54.931579+05
414	2	181	3	0	0	0	3	2026-08-05 23:30:54.931579+05
415	2	182	6	0	0	0	3	2026-08-05 23:30:54.931579+05
416	2	183	9	0	0	0	3	2026-08-05 23:30:54.931579+05
417	2	185	15	1	0	0	3	2026-08-05 23:30:54.931579+05
418	2	186	18	0	0	0	3	2026-08-05 23:30:54.931579+05
419	2	187	21	0	0	0	3	2026-08-05 23:30:54.931579+05
420	2	188	2	0	0	0	3	2026-08-05 23:30:54.931579+05
421	2	190	8	0	0	0	3	2026-08-05 23:30:54.931579+05
422	2	191	11	0	0	0	3	2026-08-05 23:30:54.931579+05
423	2	192	14	0	0	0	3	2026-08-05 23:30:54.931579+05
424	2	205	9	0	0	0	4	2026-08-05 23:30:54.931579+05
425	2	207	15	1	0	0	4	2026-08-05 23:30:54.931579+05
426	2	208	18	0	0	0	4	2026-08-05 23:30:54.931579+05
427	2	209	21	0	0	0	4	2026-08-05 23:30:54.931579+05
428	2	210	2	0	0	0	4	2026-08-05 23:30:54.931579+05
429	2	211	5	0	0	0	4	2026-08-05 23:30:54.931579+05
430	2	212	8	0	0	0	4	2026-08-05 23:30:54.931579+05
431	2	214	0	0	0	4	4	2026-08-05 23:30:54.931579+05
432	2	215	17	0	0	0	3	2026-08-05 23:30:54.931579+05
433	2	216	20	0	0	0	3	2026-08-05 23:30:54.931579+05
434	2	217	1	0	0	0	3	2026-08-05 23:30:54.931579+05
435	2	219	7	0	0	0	3	2026-08-05 23:30:54.931579+05
436	2	220	10	0	0	0	3	2026-08-05 23:30:54.931579+05
437	2	221	13	0	0	0	3	2026-08-05 23:30:54.931579+05
438	2	222	16	0	0	0	3	2026-08-05 23:30:54.931579+05
439	2	224	0	0	0	0	3	2026-08-05 23:30:54.931579+05
440	2	225	3	0	0	0	3	2026-08-05 23:30:54.931579+05
441	2	226	6	0	0	0	3	2026-08-05 23:30:54.931579+05
442	2	227	9	0	0	0	3	2026-08-05 23:30:54.931579+05
443	2	228	12	0	0	0	3	2026-08-05 23:30:54.931579+05
444	2	229	15	1	0	0	3	2026-08-05 23:30:54.931579+05
445	2	231	21	0	0	0	3	2026-08-05 23:30:54.931579+05
446	2	232	2	0	0	0	3	2026-08-05 23:30:54.931579+05
447	2	233	5	0	0	0	3	2026-08-05 23:30:54.931579+05
448	2	234	8	0	0	0	3	2026-08-05 23:30:54.931579+05
449	2	236	14	0	0	0	4	2026-08-05 23:30:54.931579+05
450	2	237	0	0	0	0	4	2026-08-05 23:30:54.931579+05
451	2	238	20	0	0	0	4	2026-08-05 23:30:54.931579+05
452	2	239	1	0	0	0	4	2026-08-05 23:30:54.931579+05
453	2	241	7	0	0	0	4	2026-08-05 23:30:54.931579+05
454	2	242	10	0	0	0	4	2026-08-05 23:30:54.931579+05
455	2	243	13	0	0	0	4	2026-08-05 23:30:54.931579+05
456	2	244	16	0	0	0	4	2026-08-05 23:30:54.931579+05
457	2	245	19	0	0	0	4	2026-08-05 23:30:54.931579+05
458	2	246	0	0	0	0	4	2026-08-05 23:30:54.931579+05
459	2	248	6	0	0	0	4	2026-08-05 23:30:54.931579+05
460	2	249	9	0	0	0	4	2026-08-05 23:30:54.931579+05
461	2	250	12	0	0	0	4	2026-08-05 23:30:54.931579+05
462	2	251	0	0	0	0	4	2026-08-05 23:30:54.931579+05
463	2	253	21	0	0	0	4	2026-08-05 23:30:54.931579+05
464	2	254	2	0	0	0	4	2026-08-05 23:30:54.931579+05
465	2	255	5	0	0	0	4	2026-08-05 23:30:54.931579+05
466	2	256	8	0	1	0	4	2026-08-05 23:30:54.931579+05
467	2	258	14	0	0	0	4	2026-08-05 23:30:54.931579+05
468	2	259	17	0	0	0	4	2026-08-05 23:30:54.931579+05
469	2	260	20	0	0	0	4	2026-08-05 23:30:54.931579+05
470	2	261	1	0	0	0	4	2026-08-05 23:30:54.931579+05
471	2	262	4	1	0	0	4	2026-08-05 23:30:54.931579+05
472	2	263	7	0	0	0	4	2026-08-05 23:30:54.931579+05
473	2	265	13	0	0	0	3	2026-08-05 23:30:54.931579+05
474	2	266	16	0	0	0	3	2026-08-05 23:30:54.931579+05
475	2	267	19	0	0	0	3	2026-08-05 23:30:54.931579+05
476	2	268	0	0	0	4	3	2026-08-05 23:30:54.931579+05
477	2	270	6	0	0	0	3	2026-08-05 23:30:54.931579+05
478	2	271	9	0	0	0	3	2026-08-05 23:30:54.931579+05
479	2	272	12	0	0	0	3	2026-08-05 23:30:54.931579+05
480	2	273	15	1	0	0	3	2026-08-05 23:30:54.931579+05
481	2	275	21	0	0	0	3	2026-08-05 23:30:54.931579+05
482	2	276	2	0	0	0	3	2026-08-05 23:30:54.931579+05
483	2	277	5	0	0	0	3	2026-08-05 23:30:54.931579+05
484	2	278	8	0	0	0	3	2026-08-05 23:30:54.931579+05
485	2	279	11	0	0	0	3	2026-08-05 23:30:54.931579+05
486	2	280	14	0	0	0	3	2026-08-05 23:30:54.931579+05
487	2	282	20	0	0	0	3	2026-08-05 23:30:54.931579+05
488	2	283	1	0	0	0	3	2026-08-05 23:30:54.931579+05
489	2	284	4	1	0	0	3	2026-08-05 23:30:54.931579+05
490	2	285	7	0	0	0	3	2026-08-05 23:30:54.931579+05
491	2	287	13	0	0	0	3	2026-08-05 23:30:54.931579+05
492	2	288	0	0	0	0	3	2026-08-05 23:30:54.931579+05
493	2	289	19	0	0	0	3	2026-08-05 23:30:54.931579+05
494	2	290	0	0	0	0	3	2026-08-05 23:30:54.931579+05
495	2	292	6	0	0	0	3	2026-08-05 23:30:54.931579+05
496	2	293	9	0	0	0	3	2026-08-05 23:30:54.931579+05
497	2	294	12	0	0	0	3	2026-08-05 23:30:54.931579+05
498	2	295	15	1	0	0	3	2026-08-05 23:30:54.931579+05
499	2	296	18	0	0	0	3	2026-08-05 23:30:54.931579+05
500	2	297	21	0	0	0	4	2026-08-05 23:30:54.931579+05
501	2	299	5	0	0	0	4	2026-08-05 23:30:54.931579+05
502	2	300	8	0	0	0	4	2026-08-05 23:30:54.931579+05
503	2	301	11	0	0	0	4	2026-08-05 23:30:54.931579+05
504	2	302	14	0	0	0	4	2026-08-05 23:30:54.931579+05
505	2	304	20	0	0	0	4	2026-08-05 23:30:54.931579+05
506	2	305	1	0	0	0	4	2026-08-05 23:30:54.931579+05
507	2	306	4	1	0	0	4	2026-08-05 23:30:54.931579+05
508	2	307	7	0	0	0	4	2026-08-05 23:30:54.931579+05
509	2	309	13	0	0	0	4	2026-08-05 23:30:54.931579+05
510	2	310	16	0	0	0	4	2026-08-05 23:30:54.931579+05
511	2	311	19	0	0	0	4	2026-08-05 23:30:54.931579+05
512	2	312	0	0	0	0	4	2026-08-05 23:30:54.931579+05
513	2	313	3	0	0	0	4	2026-08-05 23:30:54.931579+05
514	2	314	6	0	0	0	4	2026-08-05 23:30:54.931579+05
515	2	316	12	0	0	0	4	2026-08-05 23:30:54.931579+05
516	2	317	15	1	0	0	4	2026-08-05 23:30:54.931579+05
517	2	318	18	0	0	0	4	2026-08-05 23:30:54.931579+05
518	2	319	21	0	0	0	4	2026-08-05 23:30:54.931579+05
519	2	321	5	0	0	0	4	2026-08-05 23:30:54.931579+05
520	2	322	8	0	0	0	4	2026-08-05 23:30:54.931579+05
521	2	323	11	0	0	0	4	2026-08-05 23:30:54.931579+05
522	2	324	14	0	0	0	4	2026-08-05 23:30:54.931579+05
523	2	326	20	0	0	0	4	2026-08-05 23:30:54.931579+05
524	2	327	1	0	0	3	4	2026-08-05 23:30:54.931579+05
525	2	328	4	1	0	0	4	2026-08-05 23:30:54.931579+05
526	2	329	7	0	0	0	4	2026-08-05 23:30:54.931579+05
527	3	1	18	0	0	0	4	2026-08-05 23:30:54.931579+05
528	3	2	21	0	0	0	4	2026-08-05 23:30:54.931579+05
529	3	3	2	0	0	0	4	2026-08-05 23:30:54.931579+05
530	3	4	5	0	0	0	4	2026-08-05 23:30:54.931579+05
531	3	6	0	0	0	4	4	2026-08-05 23:30:54.931579+05
532	3	7	14	0	0	0	4	2026-08-05 23:30:54.931579+05
533	3	8	17	1	0	0	4	2026-08-05 23:30:54.931579+05
534	3	9	20	0	0	0	4	2026-08-05 23:30:54.931579+05
535	3	11	4	0	0	0	4	2026-08-05 23:30:54.931579+05
536	3	12	7	0	0	0	4	2026-08-05 23:30:54.931579+05
537	3	13	10	0	0	0	3	2026-08-05 23:30:54.931579+05
538	3	14	13	0	0	0	3	2026-08-05 23:30:54.931579+05
539	3	16	19	0	0	0	3	2026-08-05 23:30:54.931579+05
540	3	17	0	0	0	0	3	2026-08-05 23:30:54.931579+05
541	3	18	3	0	0	0	3	2026-08-05 23:30:54.931579+05
542	3	19	6	1	0	0	3	2026-08-05 23:30:54.931579+05
543	3	20	9	0	0	0	3	2026-08-05 23:30:54.931579+05
544	3	21	12	0	0	0	3	2026-08-05 23:30:54.931579+05
545	3	23	18	0	0	0	4	2026-08-05 23:30:54.931579+05
546	3	24	21	0	0	0	4	2026-08-05 23:30:54.931579+05
547	3	25	0	0	0	3	4	2026-08-05 23:30:54.931579+05
548	3	26	5	0	0	0	4	2026-08-05 23:30:54.931579+05
549	3	28	11	0	0	0	4	2026-08-05 23:30:54.931579+05
550	3	29	14	0	0	0	4	2026-08-05 23:30:54.931579+05
551	3	30	17	1	0	0	4	2026-08-05 23:30:54.931579+05
552	3	31	20	0	0	0	4	2026-08-05 23:30:54.931579+05
553	3	33	4	0	0	0	4	2026-08-05 23:30:54.931579+05
554	3	34	7	0	0	0	4	2026-08-05 23:30:54.931579+05
555	3	35	10	0	0	0	4	2026-08-05 23:30:54.931579+05
556	3	36	13	0	0	0	4	2026-08-05 23:30:54.931579+05
557	3	37	16	0	0	0	4	2026-08-05 23:30:54.931579+05
558	3	38	19	0	0	0	4	2026-08-05 23:30:54.931579+05
559	3	40	3	0	0	0	4	2026-08-05 23:30:54.931579+05
560	3	41	6	1	0	0	4	2026-08-05 23:30:54.931579+05
561	3	42	9	0	0	0	4	2026-08-05 23:30:54.931579+05
562	3	43	12	0	0	0	4	2026-08-05 23:30:54.931579+05
563	3	45	18	0	0	0	4	2026-08-05 23:30:54.931579+05
564	3	46	21	0	0	0	4	2026-08-05 23:30:54.931579+05
565	3	47	2	0	0	0	4	2026-08-05 23:30:54.931579+05
566	3	48	5	0	0	0	4	2026-08-05 23:30:54.931579+05
567	3	50	11	0	0	0	4	2026-08-05 23:30:54.931579+05
568	3	51	14	0	0	0	4	2026-08-05 23:30:54.931579+05
569	3	52	17	1	0	0	4	2026-08-05 23:30:54.931579+05
570	3	53	20	0	0	0	4	2026-08-05 23:30:54.931579+05
571	3	54	1	0	0	0	4	2026-08-05 23:30:54.931579+05
572	3	55	4	0	0	0	4	2026-08-05 23:30:54.931579+05
573	3	57	10	0	0	0	4	2026-08-05 23:30:54.931579+05
574	3	58	13	0	0	0	4	2026-08-05 23:30:54.931579+05
575	3	59	16	0	0	0	4	2026-08-05 23:30:54.931579+05
576	3	60	19	0	0	0	4	2026-08-05 23:30:54.931579+05
577	3	62	0	0	0	0	4	2026-08-05 23:30:54.931579+05
578	3	63	6	1	0	0	4	2026-08-05 23:30:54.931579+05
579	3	64	9	0	0	0	4	2026-08-05 23:30:54.931579+05
580	3	65	12	0	0	0	4	2026-08-05 23:30:54.931579+05
581	3	67	18	0	0	0	4	2026-08-05 23:30:54.931579+05
582	3	68	21	0	0	0	4	2026-08-05 23:30:54.931579+05
583	3	69	2	0	0	0	4	2026-08-05 23:30:54.931579+05
584	3	70	5	0	0	0	4	2026-08-05 23:30:54.931579+05
585	3	71	8	0	0	0	4	2026-08-05 23:30:54.931579+05
586	3	72	11	0	0	0	4	2026-08-05 23:30:54.931579+05
587	3	74	17	1	0	0	4	2026-08-05 23:30:54.931579+05
588	3	75	20	0	0	0	4	2026-08-05 23:30:54.931579+05
589	3	76	1	0	0	0	4	2026-08-05 23:30:54.931579+05
590	3	77	4	0	0	0	4	2026-08-05 23:30:54.931579+05
591	3	79	10	0	0	0	4	2026-08-05 23:30:54.931579+05
592	3	80	13	0	0	0	4	2026-08-05 23:30:54.931579+05
593	3	81	16	0	0	0	4	2026-08-05 23:30:54.931579+05
594	3	82	19	0	0	0	4	2026-08-05 23:30:54.931579+05
595	3	84	3	0	0	0	4	2026-08-05 23:30:54.931579+05
596	3	85	6	1	0	0	4	2026-08-05 23:30:54.931579+05
597	3	86	9	0	0	0	4	2026-08-05 23:30:54.931579+05
598	3	87	12	0	0	0	4	2026-08-05 23:30:54.931579+05
599	3	88	15	0	0	0	4	2026-08-05 23:30:54.931579+05
600	3	89	18	0	0	0	4	2026-08-05 23:30:54.931579+05
601	3	91	2	0	0	0	4	2026-08-05 23:30:54.931579+05
602	3	92	5	0	0	0	4	2026-08-05 23:30:54.931579+05
603	3	93	8	0	0	0	4	2026-08-05 23:30:54.931579+05
604	3	94	11	0	0	0	4	2026-08-05 23:30:54.931579+05
605	3	96	17	1	0	0	4	2026-08-05 23:30:54.931579+05
606	3	97	20	0	0	0	4	2026-08-05 23:30:54.931579+05
607	3	98	1	0	0	0	3	2026-08-05 23:30:54.931579+05
608	3	99	0	0	0	4	3	2026-08-05 23:30:54.931579+05
609	3	101	10	0	0	0	3	2026-08-05 23:30:54.931579+05
610	3	102	13	0	0	0	3	2026-08-05 23:30:54.931579+05
611	3	103	16	0	0	0	3	2026-08-05 23:30:54.931579+05
612	3	104	19	0	0	0	3	2026-08-05 23:30:54.931579+05
613	3	105	0	0	0	4	3	2026-08-05 23:30:54.931579+05
614	3	106	3	0	0	0	3	2026-08-05 23:30:54.931579+05
615	3	108	9	0	0	0	3	2026-08-05 23:30:54.931579+05
616	3	109	12	0	0	0	4	2026-08-05 23:30:54.931579+05
617	3	110	15	0	0	0	4	2026-08-05 23:30:54.931579+05
618	3	111	18	0	0	0	4	2026-08-05 23:30:54.931579+05
619	3	113	2	0	0	0	4	2026-08-05 23:30:54.931579+05
620	3	114	5	0	0	0	4	2026-08-05 23:30:54.931579+05
621	3	115	8	0	0	0	4	2026-08-05 23:30:54.931579+05
622	3	116	11	0	0	0	4	2026-08-05 23:30:54.931579+05
623	3	118	17	1	0	0	4	2026-08-05 23:30:54.931579+05
624	3	119	20	0	0	0	4	2026-08-05 23:30:54.931579+05
625	3	120	1	0	0	0	4	2026-08-05 23:30:54.931579+05
626	3	121	4	0	0	0	3	2026-08-05 23:30:54.931579+05
627	3	122	7	0	0	0	3	2026-08-05 23:30:54.931579+05
628	3	123	10	0	0	0	3	2026-08-05 23:30:54.931579+05
629	3	125	16	0	0	0	3	2026-08-05 23:30:54.931579+05
630	3	126	19	0	1	0	3	2026-08-05 23:30:54.931579+05
631	3	127	0	0	0	0	3	2026-08-05 23:30:54.931579+05
632	3	128	3	0	0	0	3	2026-08-05 23:30:54.931579+05
633	3	130	9	0	0	0	3	2026-08-05 23:30:54.931579+05
634	3	131	12	0	0	0	3	2026-08-05 23:30:54.931579+05
635	3	132	15	0	0	0	3	2026-08-05 23:30:54.931579+05
636	3	133	18	0	0	0	3	2026-08-05 23:30:54.931579+05
637	3	135	2	0	0	0	3	2026-08-05 23:30:54.931579+05
638	3	136	0	0	0	0	3	2026-08-05 23:30:54.931579+05
639	3	137	8	0	0	0	3	2026-08-05 23:30:54.931579+05
640	3	138	11	0	0	0	3	2026-08-05 23:30:54.931579+05
641	3	139	14	0	0	0	3	2026-08-05 23:30:54.931579+05
642	3	140	17	1	0	0	3	2026-08-05 23:30:54.931579+05
643	3	142	1	0	0	0	3	2026-08-05 23:30:54.931579+05
644	3	143	4	0	0	0	3	2026-08-05 23:30:54.931579+05
645	3	144	7	0	0	0	3	2026-08-05 23:30:54.931579+05
646	3	145	10	0	0	0	3	2026-08-05 23:30:54.931579+05
647	3	147	16	0	0	0	3	2026-08-05 23:30:54.931579+05
648	3	148	19	0	0	0	3	2026-08-05 23:30:54.931579+05
649	3	149	0	0	0	0	3	2026-08-05 23:30:54.931579+05
650	3	150	3	0	0	0	3	2026-08-05 23:30:54.931579+05
651	3	152	9	0	0	0	3	2026-08-05 23:30:54.931579+05
652	3	153	12	0	0	0	3	2026-08-05 23:30:54.931579+05
653	3	154	15	0	0	0	3	2026-08-05 23:30:54.931579+05
654	3	155	18	0	0	0	3	2026-08-05 23:30:54.931579+05
655	3	156	21	0	0	0	3	2026-08-05 23:30:54.931579+05
656	3	157	2	0	0	0	3	2026-08-05 23:30:54.931579+05
657	3	159	8	0	0	0	3	2026-08-05 23:30:54.931579+05
658	3	160	3	0	0	0	3	2026-08-05 23:30:54.931579+05
659	3	161	14	0	0	0	3	2026-08-05 23:30:54.931579+05
660	3	162	17	1	0	0	3	2026-08-05 23:30:54.931579+05
661	3	164	1	0	0	0	3	2026-08-05 23:30:54.931579+05
662	3	165	4	0	0	0	3	2026-08-05 23:30:54.931579+05
663	3	166	7	0	0	0	3	2026-08-05 23:30:54.931579+05
664	3	167	10	0	0	0	3	2026-08-05 23:30:54.931579+05
665	3	169	16	0	1	0	3	2026-08-05 23:30:54.931579+05
666	3	170	19	0	0	0	3	2026-08-05 23:30:54.931579+05
667	3	171	0	0	0	4	3	2026-08-05 23:30:54.931579+05
668	3	172	3	0	0	0	3	2026-08-05 23:30:54.931579+05
669	3	173	0	0	0	0	3	2026-08-05 23:30:54.931579+05
670	3	174	9	0	0	0	3	2026-08-05 23:30:54.931579+05
671	3	176	15	0	0	0	3	2026-08-05 23:30:54.931579+05
672	3	177	18	0	0	0	3	2026-08-05 23:30:54.931579+05
673	3	178	21	0	0	0	3	2026-08-05 23:30:54.931579+05
674	3	179	2	0	0	3	3	2026-08-05 23:30:54.931579+05
675	3	181	8	0	0	0	3	2026-08-05 23:30:54.931579+05
676	3	182	11	0	0	0	3	2026-08-05 23:30:54.931579+05
677	3	183	14	0	0	0	3	2026-08-05 23:30:54.931579+05
678	3	184	17	1	0	0	3	2026-08-05 23:30:54.931579+05
679	3	186	1	0	0	3	3	2026-08-05 23:30:54.931579+05
680	3	187	4	0	0	0	3	2026-08-05 23:30:54.931579+05
681	3	188	7	0	0	0	3	2026-08-05 23:30:54.931579+05
682	3	189	10	0	0	0	3	2026-08-05 23:30:54.931579+05
683	3	190	13	0	0	0	3	2026-08-05 23:30:54.931579+05
684	3	191	16	0	0	0	3	2026-08-05 23:30:54.931579+05
685	3	205	14	0	0	0	4	2026-08-05 23:30:54.931579+05
686	3	206	17	1	0	0	4	2026-08-05 23:30:54.931579+05
687	3	207	20	0	0	0	4	2026-08-05 23:30:54.931579+05
688	3	208	1	0	0	0	4	2026-08-05 23:30:54.931579+05
689	3	210	0	0	0	4	4	2026-08-05 23:30:54.931579+05
690	3	211	10	0	0	0	4	2026-08-05 23:30:54.931579+05
691	3	212	13	0	1	0	4	2026-08-05 23:30:54.931579+05
692	3	213	16	0	0	0	4	2026-08-05 23:30:54.931579+05
693	3	215	0	0	0	0	3	2026-08-05 23:30:54.931579+05
694	3	216	3	0	0	0	3	2026-08-05 23:30:54.931579+05
695	3	217	6	1	0	0	3	2026-08-05 23:30:54.931579+05
696	3	218	9	0	0	0	3	2026-08-05 23:30:54.931579+05
697	3	220	15	0	0	0	3	2026-08-05 23:30:54.931579+05
698	3	221	18	0	0	0	3	2026-08-05 23:30:54.931579+05
699	3	222	21	0	0	0	3	2026-08-05 23:30:54.931579+05
700	3	223	2	0	0	0	3	2026-08-05 23:30:54.931579+05
701	3	224	5	0	0	0	3	2026-08-05 23:30:54.931579+05
702	3	225	8	0	0	0	3	2026-08-05 23:30:54.931579+05
703	3	227	14	0	0	0	3	2026-08-05 23:30:54.931579+05
704	3	228	17	1	0	0	3	2026-08-05 23:30:54.931579+05
705	3	229	20	0	0	0	3	2026-08-05 23:30:54.931579+05
706	3	230	1	0	0	0	3	2026-08-05 23:30:54.931579+05
707	3	232	7	0	0	0	3	2026-08-05 23:30:54.931579+05
708	3	233	10	0	0	0	3	2026-08-05 23:30:54.931579+05
709	3	234	13	0	0	0	3	2026-08-05 23:30:54.931579+05
710	3	235	16	0	0	0	4	2026-08-05 23:30:54.931579+05
711	3	237	0	0	0	4	4	2026-08-05 23:30:54.931579+05
712	3	238	3	0	0	0	4	2026-08-05 23:30:54.931579+05
713	3	239	6	1	0	0	4	2026-08-05 23:30:54.931579+05
714	3	240	9	0	0	0	4	2026-08-05 23:30:54.931579+05
715	3	241	12	0	0	0	4	2026-08-05 23:30:54.931579+05
716	3	242	15	0	0	0	4	2026-08-05 23:30:54.931579+05
717	3	244	21	0	0	0	4	2026-08-05 23:30:54.931579+05
718	3	245	2	0	0	0	4	2026-08-05 23:30:54.931579+05
719	3	246	5	0	0	0	4	2026-08-05 23:30:54.931579+05
720	3	247	0	0	0	0	4	2026-08-05 23:30:54.931579+05
721	3	249	14	0	0	0	4	2026-08-05 23:30:54.931579+05
722	3	250	17	1	0	0	4	2026-08-05 23:30:54.931579+05
723	3	251	20	0	0	0	4	2026-08-05 23:30:54.931579+05
724	3	252	1	0	0	0	4	2026-08-05 23:30:54.931579+05
725	3	254	7	0	0	0	4	2026-08-05 23:30:54.931579+05
726	3	255	10	0	1	0	4	2026-08-05 23:30:54.931579+05
727	3	256	13	0	0	0	4	2026-08-05 23:30:54.931579+05
728	3	257	16	0	0	0	4	2026-08-05 23:30:54.931579+05
729	3	258	19	0	0	0	4	2026-08-05 23:30:54.931579+05
730	3	259	0	0	0	0	4	2026-08-05 23:30:54.931579+05
731	3	261	6	1	0	0	4	2026-08-05 23:30:54.931579+05
732	3	262	9	0	0	0	4	2026-08-05 23:30:54.931579+05
733	3	263	12	0	0	0	4	2026-08-05 23:30:54.931579+05
734	3	264	15	0	0	0	4	2026-08-05 23:30:54.931579+05
735	3	266	21	0	0	0	3	2026-08-05 23:30:54.931579+05
736	3	267	2	0	0	0	3	2026-08-05 23:30:54.931579+05
737	3	268	5	0	0	0	3	2026-08-05 23:30:54.931579+05
738	3	269	8	0	0	0	3	2026-08-05 23:30:54.931579+05
739	3	271	14	0	0	0	3	2026-08-05 23:30:54.931579+05
740	3	272	17	1	0	0	3	2026-08-05 23:30:54.931579+05
741	3	273	20	0	0	0	3	2026-08-05 23:30:54.931579+05
742	3	274	1	0	0	0	3	2026-08-05 23:30:54.931579+05
743	3	275	4	0	0	0	3	2026-08-05 23:30:54.931579+05
744	3	276	7	0	0	0	3	2026-08-05 23:30:54.931579+05
745	3	278	13	0	0	0	3	2026-08-05 23:30:54.931579+05
746	3	279	16	0	0	0	3	2026-08-05 23:30:54.931579+05
747	3	280	19	0	0	0	3	2026-08-05 23:30:54.931579+05
748	3	281	0	0	0	0	3	2026-08-05 23:30:54.931579+05
749	3	297	4	0	0	0	4	2026-08-05 23:30:54.931579+05
750	3	298	7	0	1	0	4	2026-08-05 23:30:54.931579+05
751	3	300	13	0	0	0	4	2026-08-05 23:30:54.931579+05
752	3	301	16	0	0	0	4	2026-08-05 23:30:54.931579+05
753	3	302	19	0	0	0	4	2026-08-05 23:30:54.931579+05
754	3	303	0	0	0	4	4	2026-08-05 23:30:54.931579+05
755	3	305	6	1	0	0	4	2026-08-05 23:30:54.931579+05
756	3	306	9	0	0	0	4	2026-08-05 23:30:54.931579+05
757	3	307	12	0	0	0	4	2026-08-05 23:30:54.931579+05
758	3	308	15	0	0	0	4	2026-08-05 23:30:54.931579+05
759	3	309	18	0	0	0	4	2026-08-05 23:30:54.931579+05
760	3	310	21	0	0	0	4	2026-08-05 23:30:54.931579+05
761	3	312	5	0	0	0	4	2026-08-05 23:30:54.931579+05
762	3	313	8	0	0	0	4	2026-08-05 23:30:54.931579+05
763	3	314	11	0	0	0	4	2026-08-05 23:30:54.931579+05
764	3	315	14	0	0	0	4	2026-08-05 23:30:54.931579+05
765	3	317	20	0	0	0	4	2026-08-05 23:30:54.931579+05
766	3	318	1	0	0	0	4	2026-08-05 23:30:54.931579+05
767	3	319	4	0	0	0	4	2026-08-05 23:30:54.931579+05
768	3	320	7	0	0	0	4	2026-08-05 23:30:54.931579+05
769	3	322	13	0	0	0	4	2026-08-05 23:30:54.931579+05
770	3	323	16	0	0	0	4	2026-08-05 23:30:54.931579+05
771	3	324	19	0	0	0	4	2026-08-05 23:30:54.931579+05
772	3	325	0	0	0	0	4	2026-08-05 23:30:54.931579+05
773	3	326	3	0	0	0	4	2026-08-05 23:30:54.931579+05
774	3	327	6	1	0	0	4	2026-08-05 23:30:54.931579+05
775	3	329	12	0	0	0	4	2026-08-05 23:30:54.931579+05
776	3	337	14	0	0	0	4	2026-08-05 23:30:54.931579+05
777	3	339	20	0	0	0	4	2026-08-05 23:30:54.931579+05
778	3	340	1	0	0	3	4	2026-08-05 23:30:54.931579+05
779	3	341	4	0	0	0	4	2026-08-05 23:30:54.931579+05
780	3	342	7	0	0	0	4	2026-08-05 23:30:54.931579+05
781	3	343	10	0	0	0	4	2026-08-05 23:30:54.931579+05
782	3	344	13	0	0	0	4	2026-08-05 23:30:54.931579+05
783	3	346	19	0	0	0	4	2026-08-05 23:30:54.931579+05
784	3	347	0	0	0	3	4	2026-08-05 23:30:54.931579+05
\.


--
-- Data for Name: branches; Type: TABLE DATA; Schema: clothing_store; Owner: postgres
--

COPY clothing_store.branches (branch_id, branch_code, branch_name, city, address, is_active) FROM stdin;
1	LHR-GLB-01	Gulberg Flagship	Lahore	MM Alam Road, Gulberg III	t
2	ISB-F7-01	F-7 Store	Islamabad	Jinnah Super Market, F-7	t
3	KHI-CLF-01	Clifton Store	Karachi	Block 4, Clifton	t
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: clothing_store; Owner: postgres
--

COPY clothing_store.categories (category_id, parent_category_id, category_name, category_code, description, is_active) FROM stdin;
1	\N	Shirts	SHIRTS	Upper-body clothing	t
2	1	Formal Shirts	FORMAL_SHIRTS	Office and formal shirts	t
3	1	Cotton Shirts	COTTON_SHIRTS	Everyday cotton shirts	t
4	1	T-Shirts	TSHIRTS	Casual short- and long-sleeve tees	t
5	1	Polo Shirts	POLO_SHIRTS	Collared polo shirts	t
6	\N	Pants	PANTS	Lower-body clothing	t
7	6	Jeans	JEANS	Denim jeans	t
8	6	Cotton Pants	COTTON_PANTS	Cotton chinos and casual pants	t
9	6	Trousers	TROUSERS	Formal and smart trousers	t
10	6	Shorts	SHORTS	Casual and denim shorts	t
11	6	Cargo Pants	CARGO_PANTS	Utility cargo pants	t
12	\N	Activewear	ACTIVEWEAR	Gym and sports clothing	t
13	12	Gym Wear	GYM_WEAR	Gym tops and bottoms	t
14	12	Track Pants	TRACK_PANTS	Training and track pants	t
15	12	Hoodies	HOODIES	Sports and casual hoodies	t
\.


--
-- Data for Name: colors; Type: TABLE DATA; Schema: clothing_store; Owner: postgres
--

COPY clothing_store.colors (color_id, color_name, color_code, hex_code) FROM stdin;
1	Black	BLACK	#111111
2	White	WHITE	#F5F5F5
3	Navy Blue	NAVY	#1B2A49
4	Sky Blue	SKY_BLUE	#77B5E8
5	Olive Green	OLIVE	#66704A
6	Beige	BEIGE	#D7C2A3
7	Charcoal	CHARCOAL	#41444B
8	Grey	GREY	#8C8C8C
9	Maroon	MAROON	#7A1F36
10	Brown	BROWN	#795548
11	Denim Blue	DENIM_BLUE	#3D5A80
12	Forest Green	FOREST_GREEN	#285943
13	Light Blue	light_blue	#888888
14	Pale Blue	pale_blue	#888888
15	Navy	navy	#888888
16	Light Gray	light_gray	#888888
17	Cream	cream	#888888
18	Peach	peach	#888888
19	Sand Beige	sand_beige	#888888
20	Neon Green	neon_green	#888888
21	Neon Orange	neon_orange	#888888
22	Neon Yellow	neon_yellow	#888888
23	Medium Blue	medium_blue	#888888
24	Dark Blue	dark_blue	#888888
25	Khaki	khaki	#888888
26	Olive	olive	#888888
27	Stone	stone	#888888
28	Taupe	taupe	#888888
29	Dark Khaki	dark_khaki	#888888
30	Black With Teal Accents	black_with_teal_accents	#888888
31	Navy With Blue Accents	navy_with_blue_accents	#888888
32	Gray With Lime Accents	gray_with_lime_accents	#888888
33	Black With Orange Accents	black_with_orange_accents	#888888
34	Charcoal With Teal Accents	charcoal_with_teal_accents	#888888
35	Navy With White Accents	navy_with_white_accents	#888888
36	Black With Teal Details	black_with_teal_details	#888888
37	Charcoal With White Details	charcoal_with_white_details	#888888
38	Navy With Red Details	navy_with_red_details	#888888
39	Burgundy	burgundy	#888888
40	Heather Gray	heather_gray	#888888
41	Dark Gray	dark_gray	#888888
42	Black With Blue Accents	black_with_blue_accents	#888888
43	Black With Red Accents	black_with_red_accents	#888888
44	Navy With Gray Accents	navy_with_gray_accents	#888888
\.


--
-- Data for Name: product_images; Type: TABLE DATA; Schema: clothing_store; Owner: postgres
--

COPY clothing_store.product_images (image_id, product_id, image_path, alt_text, display_order, is_primary, color_id) FROM stdin;
53	1	https://unsplash.com/photos/man-in-white-dress-shirt-Kh9848XlZe8	Man in white dress shirt	0	t	2
54	1	https://unsplash.com/photos/young-man-in-a-light-blue-shirt-looking-back-OYc2VNmIstA	Young man in a light blue shirt	0	f	13
55	1	https://unsplash.com/photos/mens-black-dress-shirt-hNoSCxPWYII	Men's black dress shirt	0	f	1
56	2	https://unsplash.com/photos/a-blue-shirt-hanging-on-a-white-wall-vcTKFYNZop4	Blue shirt hanging on wall	0	t	13
57	2	https://unsplash.com/photos/stylish-woman-in-white-linen-shirt-and-shorts-outdoors-EFCmSAeIT8E	White linen shirt outdoors	0	f	2
58	2	https://unsplash.com/photos/man-in-beige-collared-shirt-iUhzZ3tUmXE	Man in beige collared shirt	0	f	6
59	3	https://unsplash.com/photos/a-blue-shirt-hanging-on-a-wooden-stand-HGqPrIJAOBY	Blue shirt on wooden stand	0	t	14
60	3	https://unsplash.com/photos/mens-white-button-up-collared-shirt-XYeKylILW5I	Men's white button-up shirt	0	f	2
61	3	https://unsplash.com/photos/mens-blue-button-up-shirt-pyTOsURAO7M	Men's blue button-up shirt	0	f	15
62	4	https://unsplash.com/photos/man-wearing-black-t-shirt-with-space-vision-graphic-ksIPDQduysA	Black graphic T-shirt	0	t	1
63	4	https://unsplash.com/photos/young-man-stands-on-asphalt-adjusting-his-dark-graphic-t-shirt-AK87QT6e2pc	Dark graphic T-shirt	0	f	7
64	4	https://unsplash.com/photos/man-wearing-a-white-t-shirt-with-a-graphic-ErfVCDnGdXg	White graphic T-shirt	0	f	2
65	5	https://unsplash.com/photos/mens-white-crew-neck-plain-t-shirt-hYskLMtgGgY	Men's white crew-neck T-shirt	0	t	2
66	5	https://unsplash.com/photos/mens-black-crew-neck-t-shirt-Wm5GXRHIs1k	Men's black crew-neck T-shirt	0	f	1
67	5	https://unsplash.com/photos/man-wearing-gray-crew-neck-t-shirt-c-H-dYbFGRw	Man wearing gray crew-neck T-shirt	0	f	16
68	5	https://unsplash.com/photos/shallow-focus-photo-of-man-in-navy-blue-crew-neck-t-shirt-YpHa1VyFbt0	Man in navy crew-neck T-shirt	0	f	15
69	6	https://unsplash.com/photos/a-man-in-a-navy-polo-shirt-with-arms-crossed-126jj94OSY8	Man in navy polo shirt	0	t	15
70	6	https://unsplash.com/photos/man-wearing-white-polo-shirt-CceG6jpl19M	Man wearing white polo shirt	0	f	2
71	6	https://unsplash.com/photos/man-in-black-polo-shirt-CQgxaBhuzhA	Man in black polo shirt	0	f	1
72	6	https://unsplash.com/photos/mens-maroon-polo-shirt-vofmJUVScDE	Men's maroon polo shirt	0	f	9
73	7	https://unsplash.com/photos/man-wearing-mandarin-collared-top-near-wall-lltQWb9YbBU	Man wearing Mandarin-collared top	0	t	17
74	7	https://unsplash.com/photos/woman-in-white-shirt-against-gray-wall-4vXy06iLTO8	White shirt against gray wall	0	f	2
75	7			0	f	1
76	8			0	t	18
77	8			0	f	19
78	8	https://unsplash.com/photos/man-wearing-blue-button-up-collared-short-sleeved-shirt-jyoC-YG_c7w	Blue short-sleeved button-up shirt	0	f	13
79	23			0	t	20
80	23	https://unsplash.com/photos/a-man-leaning-against-a-wall-wearing-an-orange-shirt--rF_v9Mqz9o	Man wearing orange shirt	0	f	21
81	23	https://unsplash.com/photos/a-man-in-a-yellow-t-shirt-smiles-at-the-camera-ETer5qatBsM	Man in yellow T-shirt	0	f	22
82	9	https://unsplash.com/photos/mens-blue-denim-fitted-jeans-yAQWyn2mJi4	Men's blue fitted jeans	0	t	23
83	9	https://unsplash.com/photos/a-pair-of-dark-blue-jeans-on-a-white-background-wNP79A-_bRY	Dark-blue jeans	0	f	24
84	9	https://unsplash.com/photos/man-in-black-denim-jeans-wjulyIQi3C4	Man in black denim jeans	0	f	1
85	10	https://unsplash.com/photos/mens-blue-denim-jeans-ULtUCTC8lGg	Men's blue denim jeans	0	t	24
86	10	https://unsplash.com/photos/man-wearing-blue-denim-jeans-rJGrhGljDuc	Man wearing blue denim jeans	0	f	23
87	10	https://unsplash.com/photos/black-jeans-cY22e3ywkic	Black jeans	0	f	1
88	11	https://unsplash.com/photos/a-man-in-a-white-shirt-and-khaki-pants-standing-in-front-of-a-C1sDxiSsE-8	Man in khaki pants	0	t	25
89	11	https://unsplash.com/photos/man-wearing-blue-pants-walking-on-street-NrlHjNUqqgM	Man wearing blue pants	0	f	15
90	11			0	f	26
91	12	https://unsplash.com/photos/man-in-blue-dress-shirt-and-black-dress-pants-wearing-black-necktie-I3C5ctmT8Z0	Black dress pants	0	t	1
92	12	https://unsplash.com/photos/man-wearing-gray-dress-shirt-and-gray-pants-behind-of-black-and-red-charcoal-train-TaAT8l7X5jo	Man wearing gray pants	0	f	7
93	12	https://unsplash.com/photos/a-man-in-a-white-shirt-and-blue-pants-Ga6YYbBWa5I	Man in blue pants	0	f	15
94	13	https://unsplash.com/photos/man-in-gray-crew-neck-t-shirt-and-gray-pants-standing-on-brown-wooden-bridge-during-YnKKGzQjpTw	Man in gray pants	0	t	7
95	13	https://unsplash.com/photos/man-in-gray-button-up-shirt-and-black-pants-sitting-on-brown-rock-during-daytime-VL2RkOMiLPk	Man in black pants	0	f	1
96	13			0	f	27
97	14			0	t	5
98	14			0	f	1
99	14	https://unsplash.com/photos/man-in-black-t-shirt-and-khaki-pants-ZsUCBnNx5_0	Man in khaki cargo pants	0	f	25
100	15	https://unsplash.com/photos/person-in-blue-denim-shorts-and-gray-and-black-nike-athletic-shoes-l2q9a2MfXyU	Person in blue denim shorts	0	t	23
101	15	https://unsplash.com/photos/person-wearing-light-blue-sneakers-and-denim-shorts-mVo0wDyRMvY	Person wearing denim shorts	0	f	13
102	15			0	f	1
103	16	https://unsplash.com/photos/man-in-a-brown-pants-lFQV2lt7qcw	Man in brown pants	0	t	10
104	16			0	f	28
105	16	https://unsplash.com/photos/a-man-wearing-a-paris-shirt-and-khaki-pants-MrH9XNLmeIQ	Man wearing khaki pants	0	f	29
106	24			0	t	28
107	24			0	f	27
108	24			0	f	7
109	17	https://unsplash.com/photos/man-wearing-black-and-teal-shirt-on-sea-shore-1iCe-luOoQ4	Man wearing black and teal shirt	0	t	30
110	17	https://unsplash.com/photos/man-in-blue-crew-neck-t-shirt-and-black-pants-wearing-black-and-gray-dumbbells-5Lp7PJONCFw	Man in blue athletic T-shirt	0	f	31
111	17			0	f	32
112	18			0	t	33
113	18			0	f	34
114	18			0	f	35
115	19			0	t	36
116	19	https://unsplash.com/photos/man-in-a-gray-sweater-and-black-and-white-track-pants-TyGF7zx5T2Y	Man in black-and-white track pants	0	f	37
117	19			0	f	38
118	20	https://unsplash.com/photos/man-in-maroon-hoodie-leaning-on-wall-overlooking-sea-cQVYdkQKsvQ	Man in maroon hoodie	0	t	39
119	20	https://unsplash.com/photos/mens-black-pullover-hoodie-zf2Uwq-aFJ4	Men's black pullover hoodie	0	f	1
120	20	https://unsplash.com/photos/man-wearing-gray-pullover-hoodie-rSZ8YeNw4w4	Man wearing gray pullover hoodie	0	f	40
121	20	https://unsplash.com/photos/shallow-focus-photo-of-navy-blue-pullover-hoodie-kpO3XVLzGGg	Navy-blue pullover hoodie	0	f	15
122	21	https://unsplash.com/photos/a-man-standing-on-a-sidewalk-wearing-a-sweater-and-sweatpants-Vuyeudrim2I	Man wearing gray sweatpants	0	t	41
123	21	https://unsplash.com/photos/a-man-wearing-a-black-hoodie-and-sweatpants-48-R71Sd_d8	Man wearing black joggers	0	f	1
124	21	https://unsplash.com/photos/woman-wearing-white-crew-neck-long-sleeved-shirt-and-blue-jogger-pants-IiFB9sWi4MI	Blue jogger pants	0	f	15
125	22	https://unsplash.com/photos/mens-black-and-blue-crew-neck-shirt-vlx7Z2X5f5o	Black and blue crew-neck shirt	0	t	42
126	22	https://unsplash.com/photos/man-wearing-black-and-red-crew-neck-shirt-3mMvCsW6ZYs	Black and red crew-neck shirt	0	f	43
127	22			0	f	44
\.


--
-- Data for Name: product_variants; Type: TABLE DATA; Schema: clothing_store; Owner: postgres
--

COPY clothing_store.product_variants (variant_id, product_id, color_id, size_id, sku, barcode, cost_price, selling_price, is_active) FROM stdin;
1	1	2	2	MS-FS-001-WHI-S	8900010202001	1850.00	3490.00	t
2	1	2	3	MS-FS-001-WHI-M	8900010203002	1850.00	3490.00	t
3	1	2	4	MS-FS-001-WHI-L	8900010204003	1850.00	3490.00	t
4	1	2	5	MS-FS-001-WHI-XL	8900010205004	1850.00	3490.00	t
5	1	3	2	MS-FS-001-NAV-S	8900010302005	1850.00	3490.00	t
6	1	3	3	MS-FS-001-NAV-M	8900010303006	1850.00	3490.00	t
7	1	3	4	MS-FS-001-NAV-L	8900010304007	1850.00	3490.00	t
8	1	3	5	MS-FS-001-NAV-XL	8900010305008	1850.00	3490.00	t
9	1	4	2	MS-FS-001-SKY-S	8900010402009	1850.00	3490.00	t
10	1	4	3	MS-FS-001-SKY-M	8900010403010	1850.00	3490.00	t
11	1	4	4	MS-FS-001-SKY-L	8900010404011	1850.00	3490.00	t
12	1	4	5	MS-FS-001-SKY-XL	8900010405012	1850.00	3490.00	t
13	2	2	2	MS-CS-002-WHI-S	8900020202013	2100.00	4190.00	t
14	2	2	3	MS-CS-002-WHI-M	8900020203014	2100.00	4190.00	t
15	2	2	4	MS-CS-002-WHI-L	8900020204015	2100.00	4190.00	t
16	2	2	5	MS-CS-002-WHI-XL	8900020205016	2100.00	4190.00	t
17	2	6	2	MS-CS-002-BEI-S	8900020602017	2100.00	4190.00	t
18	2	6	3	MS-CS-002-BEI-M	8900020603018	2100.00	4190.00	t
19	2	6	4	MS-CS-002-BEI-L	8900020604019	2100.00	4190.00	t
20	2	6	5	MS-CS-002-BEI-XL	8900020605020	2100.00	4190.00	t
21	2	12	3	MS-CS-002-FOR-M	8900021203021	2100.00	4390.00	t
22	2	12	4	MS-CS-002-FOR-L	8900021204022	2100.00	4390.00	t
23	3	2	1	MS-CS-003-WHI-XS	8900030201023	1450.00	2890.00	t
24	3	2	2	MS-CS-003-WHI-S	8900030202024	1450.00	2890.00	t
25	3	2	3	MS-CS-003-WHI-M	8900030203025	1450.00	2890.00	t
26	3	2	4	MS-CS-003-WHI-L	8900030204026	1450.00	2890.00	t
27	3	2	5	MS-CS-003-WHI-XL	8900030205027	1450.00	2890.00	t
28	3	2	6	MS-CS-003-WHI-XXL	8900030206028	1450.00	3040.00	t
29	3	3	1	MS-CS-003-NAV-XS	8900030301029	1450.00	2890.00	t
30	3	3	2	MS-CS-003-NAV-S	8900030302030	1450.00	2890.00	t
31	3	3	3	MS-CS-003-NAV-M	8900030303031	1450.00	2890.00	t
32	3	3	4	MS-CS-003-NAV-L	8900030304032	1450.00	2890.00	t
33	3	3	5	MS-CS-003-NAV-XL	8900030305033	1450.00	2890.00	t
34	3	3	6	MS-CS-003-NAV-XXL	8900030306034	1450.00	3040.00	t
35	3	4	1	MS-CS-003-SKY-XS	8900030401035	1450.00	2890.00	t
36	3	4	2	MS-CS-003-SKY-S	8900030402036	1450.00	2890.00	t
37	3	4	3	MS-CS-003-SKY-M	8900030403037	1450.00	2890.00	t
38	3	4	4	MS-CS-003-SKY-L	8900030404038	1450.00	2890.00	t
39	3	4	5	MS-CS-003-SKY-XL	8900030405039	1450.00	2890.00	t
40	3	4	6	MS-CS-003-SKY-XXL	8900030406040	1450.00	3040.00	t
41	3	8	1	MS-CS-003-GRE-XS	8900030801041	1450.00	2890.00	t
42	3	8	2	MS-CS-003-GRE-S	8900030802042	1450.00	2890.00	t
43	3	8	3	MS-CS-003-GRE-M	8900030803043	1450.00	2890.00	t
44	3	8	4	MS-CS-003-GRE-L	8900030804044	1450.00	2890.00	t
45	3	8	5	MS-CS-003-GRE-XL	8900030805045	1450.00	2890.00	t
46	3	8	6	MS-CS-003-GRE-XXL	8900030806046	1450.00	3040.00	t
47	4	1	2	MS-TS-004-BLA-S	8900040102047	850.00	1890.00	t
48	4	1	3	MS-TS-004-BLA-M	8900040103048	850.00	1890.00	t
49	4	1	4	MS-TS-004-BLA-L	8900040104049	850.00	1890.00	t
50	4	1	5	MS-TS-004-BLA-XL	8900040105050	850.00	1890.00	t
51	4	2	2	MS-TS-004-WHI-S	8900040202051	850.00	1890.00	t
52	4	2	3	MS-TS-004-WHI-M	8900040203052	850.00	1890.00	t
53	4	2	4	MS-TS-004-WHI-L	8900040204053	850.00	1890.00	t
54	4	2	5	MS-TS-004-WHI-XL	8900040205054	850.00	1890.00	t
55	4	9	2	MS-TS-004-MAR-S	8900040902055	850.00	2090.00	t
56	4	9	3	MS-TS-004-MAR-M	8900040903056	850.00	2090.00	t
57	4	9	4	MS-TS-004-MAR-L	8900040904057	850.00	2090.00	t
58	5	1	1	MS-TS-005-BLA-XS	8900050101058	680.00	1490.00	t
59	5	1	2	MS-TS-005-BLA-S	8900050102059	680.00	1490.00	t
60	5	1	3	MS-TS-005-BLA-M	8900050103060	680.00	1490.00	t
61	5	1	4	MS-TS-005-BLA-L	8900050104061	680.00	1490.00	t
62	5	1	5	MS-TS-005-BLA-XL	8900050105062	680.00	1490.00	t
63	5	1	6	MS-TS-005-BLA-XXL	8900050106063	680.00	1640.00	t
64	5	2	1	MS-TS-005-WHI-XS	8900050201064	680.00	1490.00	t
65	5	2	2	MS-TS-005-WHI-S	8900050202065	680.00	1490.00	t
66	5	2	3	MS-TS-005-WHI-M	8900050203066	680.00	1490.00	t
67	5	2	4	MS-TS-005-WHI-L	8900050204067	680.00	1490.00	t
68	5	2	5	MS-TS-005-WHI-XL	8900050205068	680.00	1490.00	t
69	5	2	6	MS-TS-005-WHI-XXL	8900050206069	680.00	1640.00	t
70	5	7	1	MS-TS-005-CHA-XS	8900050701070	680.00	1490.00	t
71	5	7	2	MS-TS-005-CHA-S	8900050702071	680.00	1490.00	t
72	5	7	3	MS-TS-005-CHA-M	8900050703072	680.00	1490.00	t
73	5	7	4	MS-TS-005-CHA-L	8900050704073	680.00	1490.00	t
74	5	7	5	MS-TS-005-CHA-XL	8900050705074	680.00	1490.00	t
75	5	7	6	MS-TS-005-CHA-XXL	8900050706075	680.00	1640.00	t
76	5	8	1	MS-TS-005-GRE-XS	8900050801076	680.00	1490.00	t
77	5	8	2	MS-TS-005-GRE-S	8900050802077	680.00	1490.00	t
78	5	8	3	MS-TS-005-GRE-M	8900050803078	680.00	1490.00	t
79	5	8	4	MS-TS-005-GRE-L	8900050804079	680.00	1490.00	t
80	5	8	5	MS-TS-005-GRE-XL	8900050805080	680.00	1490.00	t
81	5	8	6	MS-TS-005-GRE-XXL	8900050806081	680.00	1640.00	t
82	6	2	2	MS-PL-006-WHI-S	8900060202082	1250.00	2690.00	t
83	6	2	3	MS-PL-006-WHI-M	8900060203083	1250.00	2690.00	t
84	6	2	4	MS-PL-006-WHI-L	8900060204084	1250.00	2690.00	t
85	6	2	5	MS-PL-006-WHI-XL	8900060205085	1250.00	2690.00	t
86	6	3	2	MS-PL-006-NAV-S	8900060302086	1250.00	2690.00	t
87	6	3	3	MS-PL-006-NAV-M	8900060303087	1250.00	2690.00	t
88	6	3	4	MS-PL-006-NAV-L	8900060304088	1250.00	2690.00	t
89	6	3	5	MS-PL-006-NAV-XL	8900060305089	1250.00	2690.00	t
90	6	5	2	MS-PL-006-OLI-S	8900060502090	1250.00	2690.00	t
91	6	5	3	MS-PL-006-OLI-M	8900060503091	1250.00	2690.00	t
92	6	5	4	MS-PL-006-OLI-L	8900060504092	1250.00	2690.00	t
93	6	5	5	MS-PL-006-OLI-XL	8900060505093	1250.00	2690.00	t
94	6	9	2	MS-PL-006-MAR-S	8900060902094	1250.00	2890.00	t
95	6	9	3	MS-PL-006-MAR-M	8900060903095	1250.00	2890.00	t
96	6	9	4	MS-PL-006-MAR-L	8900060904096	1250.00	2890.00	t
97	6	9	5	MS-PL-006-MAR-XL	8900060905097	1250.00	2890.00	t
98	7	2	2	MS-FS-007-WHI-S	8900070202098	2050.00	3990.00	t
99	7	2	3	MS-FS-007-WHI-M	8900070203099	2050.00	3990.00	t
100	7	2	4	MS-FS-007-WHI-L	8900070204100	2050.00	3990.00	t
101	7	2	5	MS-FS-007-WHI-XL	8900070205101	2050.00	3990.00	t
102	7	3	2	MS-FS-007-NAV-S	8900070302102	2050.00	3990.00	t
103	7	3	3	MS-FS-007-NAV-M	8900070303103	2050.00	3990.00	t
104	7	3	4	MS-FS-007-NAV-L	8900070304104	2050.00	3990.00	t
105	7	3	5	MS-FS-007-NAV-XL	8900070305105	2050.00	3990.00	t
106	7	9	2	MS-FS-007-MAR-S	8900070902106	2050.00	4190.00	t
107	7	9	3	MS-FS-007-MAR-M	8900070903107	2050.00	4190.00	t
108	7	9	4	MS-FS-007-MAR-L	8900070904108	2050.00	4190.00	t
109	8	2	2	MS-CS-008-WHI-S	8900080202109	1250.00	2590.00	t
110	8	2	3	MS-CS-008-WHI-M	8900080203110	1250.00	2590.00	t
111	8	2	4	MS-CS-008-WHI-L	8900080204111	1250.00	2590.00	t
112	8	2	5	MS-CS-008-WHI-XL	8900080205112	1250.00	2590.00	t
113	8	4	2	MS-CS-008-SKY-S	8900080402113	1250.00	2590.00	t
114	8	4	3	MS-CS-008-SKY-M	8900080403114	1250.00	2590.00	t
115	8	4	4	MS-CS-008-SKY-L	8900080404115	1250.00	2590.00	t
116	8	4	5	MS-CS-008-SKY-XL	8900080405116	1250.00	2590.00	t
117	8	6	2	MS-CS-008-BEI-S	8900080602117	1250.00	2590.00	t
118	8	6	3	MS-CS-008-BEI-M	8900080603118	1250.00	2590.00	t
119	8	6	4	MS-CS-008-BEI-L	8900080604119	1250.00	2590.00	t
120	8	6	5	MS-CS-008-BEI-XL	8900080605120	1250.00	2590.00	t
121	9	1	8	MP-JN-009-BLA-30	8900090108121	2350.00	4790.00	t
122	9	1	9	MP-JN-009-BLA-32	8900090109122	2350.00	4790.00	t
123	9	1	10	MP-JN-009-BLA-34	8900090110123	2350.00	4790.00	t
124	9	1	11	MP-JN-009-BLA-36	8900090111124	2350.00	4790.00	t
125	9	11	7	MP-JN-009-DEN-28	8900091107125	2350.00	4790.00	t
126	9	11	8	MP-JN-009-DEN-30	8900091108126	2350.00	4790.00	t
127	9	11	9	MP-JN-009-DEN-32	8900091109127	2350.00	4790.00	t
128	9	11	10	MP-JN-009-DEN-34	8900091110128	2350.00	4790.00	t
129	9	11	11	MP-JN-009-DEN-36	8900091111129	2350.00	4790.00	t
130	10	3	8	MP-JN-010-NAV-30	8900100308130	2500.00	4990.00	t
131	10	3	9	MP-JN-010-NAV-32	8900100309131	2500.00	4990.00	t
132	10	3	10	MP-JN-010-NAV-34	8900100310132	2500.00	4990.00	t
133	10	3	11	MP-JN-010-NAV-36	8900100311133	2500.00	4990.00	t
134	10	3	12	MP-JN-010-NAV-38	8900100312134	2500.00	4990.00	t
135	10	11	8	MP-JN-010-DEN-30	8900101108135	2500.00	4990.00	t
136	10	11	9	MP-JN-010-DEN-32	8900101109136	2500.00	4990.00	t
137	10	11	10	MP-JN-010-DEN-34	8900101110137	2500.00	4990.00	t
138	10	11	11	MP-JN-010-DEN-36	8900101111138	2500.00	4990.00	t
139	10	11	12	MP-JN-010-DEN-38	8900101112139	2500.00	4990.00	t
140	11	3	7	MP-CP-011-NAV-28	8900110307140	1900.00	3890.00	t
141	11	3	8	MP-CP-011-NAV-30	8900110308141	1900.00	3890.00	t
142	11	3	9	MP-CP-011-NAV-32	8900110309142	1900.00	3890.00	t
143	11	3	10	MP-CP-011-NAV-34	8900110310143	1900.00	3890.00	t
144	11	3	11	MP-CP-011-NAV-36	8900110311144	1900.00	3890.00	t
145	11	5	7	MP-CP-011-OLI-28	8900110507145	1900.00	3890.00	t
146	11	5	8	MP-CP-011-OLI-30	8900110508146	1900.00	3890.00	t
147	11	5	9	MP-CP-011-OLI-32	8900110509147	1900.00	3890.00	t
148	11	5	10	MP-CP-011-OLI-34	8900110510148	1900.00	3890.00	t
149	11	5	11	MP-CP-011-OLI-36	8900110511149	1900.00	3890.00	t
150	11	6	7	MP-CP-011-BEI-28	8900110607150	1900.00	3890.00	t
151	11	6	8	MP-CP-011-BEI-30	8900110608151	1900.00	3890.00	t
152	11	6	9	MP-CP-011-BEI-32	8900110609152	1900.00	3890.00	t
153	11	6	10	MP-CP-011-BEI-34	8900110610153	1900.00	3890.00	t
154	11	6	11	MP-CP-011-BEI-36	8900110611154	1900.00	3890.00	t
155	11	10	8	MP-CP-011-BRO-30	8900111008155	1900.00	3890.00	t
156	11	10	9	MP-CP-011-BRO-32	8900111009156	1900.00	3890.00	t
157	11	10	10	MP-CP-011-BRO-34	8900111010157	1900.00	3890.00	t
158	12	1	8	MP-TR-012-BLA-30	8900120108158	2250.00	4490.00	t
159	12	1	9	MP-TR-012-BLA-32	8900120109159	2250.00	4490.00	t
160	12	1	10	MP-TR-012-BLA-34	8900120110160	2250.00	4490.00	t
161	12	1	11	MP-TR-012-BLA-36	8900120111161	2250.00	4490.00	t
162	12	1	12	MP-TR-012-BLA-38	8900120112162	2250.00	4490.00	t
163	12	3	8	MP-TR-012-NAV-30	8900120308163	2250.00	4490.00	t
164	12	3	9	MP-TR-012-NAV-32	8900120309164	2250.00	4490.00	t
165	12	3	10	MP-TR-012-NAV-34	8900120310165	2250.00	4490.00	t
166	12	3	11	MP-TR-012-NAV-36	8900120311166	2250.00	4490.00	t
167	12	3	12	MP-TR-012-NAV-38	8900120312167	2250.00	4490.00	t
168	12	7	8	MP-TR-012-CHA-30	8900120708168	2250.00	4490.00	t
169	12	7	9	MP-TR-012-CHA-32	8900120709169	2250.00	4490.00	t
170	12	7	10	MP-TR-012-CHA-34	8900120710170	2250.00	4490.00	t
171	12	7	11	MP-TR-012-CHA-36	8900120711171	2250.00	4490.00	t
172	12	7	12	MP-TR-012-CHA-38	8900120712172	2250.00	4490.00	t
173	13	1	8	MP-TR-013-BLA-30	8900130108173	1850.00	3790.00	t
174	13	1	9	MP-TR-013-BLA-32	8900130109174	1850.00	3790.00	t
175	13	1	10	MP-TR-013-BLA-34	8900130110175	1850.00	3790.00	t
176	13	1	11	MP-TR-013-BLA-36	8900130111176	1850.00	3790.00	t
177	13	1	12	MP-TR-013-BLA-38	8900130112177	1850.00	3790.00	t
178	13	3	8	MP-TR-013-NAV-30	8900130308178	1850.00	3790.00	t
179	13	3	9	MP-TR-013-NAV-32	8900130309179	1850.00	3790.00	t
180	13	3	10	MP-TR-013-NAV-34	8900130310180	1850.00	3790.00	t
181	13	3	11	MP-TR-013-NAV-36	8900130311181	1850.00	3790.00	t
182	13	3	12	MP-TR-013-NAV-38	8900130312182	1850.00	3790.00	t
183	13	7	8	MP-TR-013-CHA-30	8900130708183	1850.00	3790.00	t
184	13	7	9	MP-TR-013-CHA-32	8900130709184	1850.00	3790.00	t
185	13	7	10	MP-TR-013-CHA-34	8900130710185	1850.00	3790.00	t
186	13	7	11	MP-TR-013-CHA-36	8900130711186	1850.00	3790.00	t
187	13	7	12	MP-TR-013-CHA-38	8900130712187	1850.00	3790.00	t
188	13	8	8	MP-TR-013-GRE-30	8900130808188	1850.00	3790.00	t
189	13	8	9	MP-TR-013-GRE-32	8900130809189	1850.00	3790.00	t
190	13	8	10	MP-TR-013-GRE-34	8900130810190	1850.00	3790.00	t
191	13	8	11	MP-TR-013-GRE-36	8900130811191	1850.00	3790.00	t
192	13	8	12	MP-TR-013-GRE-38	8900130812192	1850.00	3790.00	t
193	14	1	8	MP-CG-014-BLA-30	8900140108193	2050.00	4290.00	t
194	14	1	9	MP-CG-014-BLA-32	8900140109194	2050.00	4290.00	t
195	14	1	10	MP-CG-014-BLA-34	8900140110195	2050.00	4290.00	t
196	14	1	11	MP-CG-014-BLA-36	8900140111196	2050.00	4290.00	t
197	14	5	8	MP-CG-014-OLI-30	8900140508197	2050.00	4290.00	t
198	14	5	9	MP-CG-014-OLI-32	8900140509198	2050.00	4290.00	t
199	14	5	10	MP-CG-014-OLI-34	8900140510199	2050.00	4290.00	t
200	14	5	11	MP-CG-014-OLI-36	8900140511200	2050.00	4290.00	t
201	14	6	8	MP-CG-014-BEI-30	8900140608201	2050.00	4290.00	t
202	14	6	9	MP-CG-014-BEI-32	8900140609202	2050.00	4290.00	t
203	14	6	10	MP-CG-014-BEI-34	8900140610203	2050.00	4290.00	t
204	14	6	11	MP-CG-014-BEI-36	8900140611204	2050.00	4290.00	t
205	15	1	7	MP-SH-015-BLA-28	8900150107205	1550.00	3190.00	t
206	15	1	8	MP-SH-015-BLA-30	8900150108206	1550.00	3190.00	t
207	15	1	9	MP-SH-015-BLA-32	8900150109207	1550.00	3190.00	t
208	15	1	10	MP-SH-015-BLA-34	8900150110208	1550.00	3190.00	t
209	15	1	11	MP-SH-015-BLA-36	8900150111209	1550.00	3190.00	t
210	15	11	7	MP-SH-015-DEN-28	8900151107210	1550.00	3190.00	t
211	15	11	8	MP-SH-015-DEN-30	8900151108211	1550.00	3190.00	t
212	15	11	9	MP-SH-015-DEN-32	8900151109212	1550.00	3190.00	t
213	15	11	10	MP-SH-015-DEN-34	8900151110213	1550.00	3190.00	t
214	15	11	11	MP-SH-015-DEN-36	8900151111214	1550.00	3190.00	t
215	16	1	7	MP-CP-016-BLA-28	8900160107215	1750.00	3590.00	t
216	16	1	8	MP-CP-016-BLA-30	8900160108216	1750.00	3590.00	t
217	16	1	9	MP-CP-016-BLA-32	8900160109217	1750.00	3590.00	t
218	16	1	10	MP-CP-016-BLA-34	8900160110218	1750.00	3590.00	t
219	16	1	11	MP-CP-016-BLA-36	8900160111219	1750.00	3590.00	t
220	16	3	7	MP-CP-016-NAV-28	8900160307220	1750.00	3590.00	t
221	16	3	8	MP-CP-016-NAV-30	8900160308221	1750.00	3590.00	t
222	16	3	9	MP-CP-016-NAV-32	8900160309222	1750.00	3590.00	t
223	16	3	10	MP-CP-016-NAV-34	8900160310223	1750.00	3590.00	t
224	16	3	11	MP-CP-016-NAV-36	8900160311224	1750.00	3590.00	t
225	16	6	7	MP-CP-016-BEI-28	8900160607225	1750.00	3590.00	t
226	16	6	8	MP-CP-016-BEI-30	8900160608226	1750.00	3590.00	t
227	16	6	9	MP-CP-016-BEI-32	8900160609227	1750.00	3590.00	t
228	16	6	10	MP-CP-016-BEI-34	8900160610228	1750.00	3590.00	t
229	16	6	11	MP-CP-016-BEI-36	8900160611229	1750.00	3590.00	t
230	16	10	7	MP-CP-016-BRO-28	8900161007230	1750.00	3590.00	t
231	16	10	8	MP-CP-016-BRO-30	8900161008231	1750.00	3590.00	t
232	16	10	9	MP-CP-016-BRO-32	8900161009232	1750.00	3590.00	t
233	16	10	10	MP-CP-016-BRO-34	8900161010233	1750.00	3590.00	t
234	16	10	11	MP-CP-016-BRO-36	8900161011234	1750.00	3590.00	t
235	17	1	1	AW-GT-017-BLA-XS	8900170101235	1150.00	2490.00	t
236	17	1	2	AW-GT-017-BLA-S	8900170102236	1150.00	2490.00	t
237	17	1	3	AW-GT-017-BLA-M	8900170103237	1150.00	2490.00	t
238	17	1	4	AW-GT-017-BLA-L	8900170104238	1150.00	2490.00	t
239	17	1	5	AW-GT-017-BLA-XL	8900170105239	1150.00	2490.00	t
240	17	2	1	AW-GT-017-WHI-XS	8900170201240	1150.00	2490.00	t
241	17	2	2	AW-GT-017-WHI-S	8900170202241	1150.00	2490.00	t
242	17	2	3	AW-GT-017-WHI-M	8900170203242	1150.00	2490.00	t
243	17	2	4	AW-GT-017-WHI-L	8900170204243	1150.00	2490.00	t
244	17	2	5	AW-GT-017-WHI-XL	8900170205244	1150.00	2490.00	t
245	17	12	1	AW-GT-017-FOR-XS	8900171201245	1150.00	2690.00	t
246	17	12	2	AW-GT-017-FOR-S	8900171202246	1150.00	2690.00	t
247	17	12	3	AW-GT-017-FOR-M	8900171203247	1150.00	2690.00	t
248	17	12	4	AW-GT-017-FOR-L	8900171204248	1150.00	2690.00	t
249	17	12	5	AW-GT-017-FOR-XL	8900171205249	1150.00	2690.00	t
250	18	1	1	AW-GS-018-BLA-XS	8900180101250	1300.00	2790.00	t
251	18	1	2	AW-GS-018-BLA-S	8900180102251	1300.00	2790.00	t
252	18	1	3	AW-GS-018-BLA-M	8900180103252	1300.00	2790.00	t
253	18	1	4	AW-GS-018-BLA-L	8900180104253	1300.00	2790.00	t
254	18	1	5	AW-GS-018-BLA-XL	8900180105254	1300.00	2790.00	t
255	18	3	1	AW-GS-018-NAV-XS	8900180301255	1300.00	2790.00	t
256	18	3	2	AW-GS-018-NAV-S	8900180302256	1300.00	2790.00	t
257	18	3	3	AW-GS-018-NAV-M	8900180303257	1300.00	2790.00	t
258	18	3	4	AW-GS-018-NAV-L	8900180304258	1300.00	2790.00	t
259	18	3	5	AW-GS-018-NAV-XL	8900180305259	1300.00	2790.00	t
260	18	8	1	AW-GS-018-GRE-XS	8900180801260	1300.00	2790.00	t
261	18	8	2	AW-GS-018-GRE-S	8900180802261	1300.00	2790.00	t
262	18	8	3	AW-GS-018-GRE-M	8900180803262	1300.00	2790.00	t
263	18	8	4	AW-GS-018-GRE-L	8900180804263	1300.00	2790.00	t
264	18	8	5	AW-GS-018-GRE-XL	8900180805264	1300.00	2790.00	t
265	19	1	1	AW-TP-019-BLA-XS	8900190101265	1750.00	3590.00	t
266	19	1	2	AW-TP-019-BLA-S	8900190102266	1750.00	3590.00	t
267	19	1	3	AW-TP-019-BLA-M	8900190103267	1750.00	3590.00	t
268	19	1	4	AW-TP-019-BLA-L	8900190104268	1750.00	3590.00	t
269	19	1	5	AW-TP-019-BLA-XL	8900190105269	1750.00	3590.00	t
270	19	1	6	AW-TP-019-BLA-XXL	8900190106270	1750.00	3740.00	t
271	19	3	1	AW-TP-019-NAV-XS	8900190301271	1750.00	3590.00	t
272	19	3	2	AW-TP-019-NAV-S	8900190302272	1750.00	3590.00	t
273	19	3	3	AW-TP-019-NAV-M	8900190303273	1750.00	3590.00	t
274	19	3	4	AW-TP-019-NAV-L	8900190304274	1750.00	3590.00	t
275	19	3	5	AW-TP-019-NAV-XL	8900190305275	1750.00	3590.00	t
276	19	3	6	AW-TP-019-NAV-XXL	8900190306276	1750.00	3740.00	t
277	19	7	1	AW-TP-019-CHA-XS	8900190701277	1750.00	3590.00	t
278	19	7	2	AW-TP-019-CHA-S	8900190702278	1750.00	3590.00	t
279	19	7	3	AW-TP-019-CHA-M	8900190703279	1750.00	3590.00	t
280	19	7	4	AW-TP-019-CHA-L	8900190704280	1750.00	3590.00	t
281	19	7	5	AW-TP-019-CHA-XL	8900190705281	1750.00	3590.00	t
282	19	7	6	AW-TP-019-CHA-XXL	8900190706282	1750.00	3740.00	t
283	20	3	2	AW-HD-020-NAV-S	8900200302283	2250.00	4690.00	t
284	20	3	3	AW-HD-020-NAV-M	8900200303284	2250.00	4690.00	t
285	20	3	4	AW-HD-020-NAV-L	8900200304285	2250.00	4690.00	t
286	20	3	5	AW-HD-020-NAV-XL	8900200305286	2250.00	4690.00	t
287	20	3	6	AW-HD-020-NAV-XXL	8900200306287	2250.00	4840.00	t
288	20	7	2	AW-HD-020-CHA-S	8900200702288	2250.00	4690.00	t
289	20	7	3	AW-HD-020-CHA-M	8900200703289	2250.00	4690.00	t
290	20	7	4	AW-HD-020-CHA-L	8900200704290	2250.00	4690.00	t
291	20	7	5	AW-HD-020-CHA-XL	8900200705291	2250.00	4690.00	t
292	20	7	6	AW-HD-020-CHA-XXL	8900200706292	2250.00	4840.00	t
293	20	9	3	AW-HD-020-MAR-M	8900200903293	2250.00	4890.00	t
294	20	9	4	AW-HD-020-MAR-L	8900200904294	2250.00	4890.00	t
295	20	9	5	AW-HD-020-MAR-XL	8900200905295	2250.00	4890.00	t
296	20	9	6	AW-HD-020-MAR-XXL	8900200906296	2250.00	5040.00	t
297	21	1	1	AW-GJ-021-BLA-XS	8900210101297	1600.00	3290.00	t
298	21	1	2	AW-GJ-021-BLA-S	8900210102298	1600.00	3290.00	t
299	21	1	3	AW-GJ-021-BLA-M	8900210103299	1600.00	3290.00	t
300	21	1	4	AW-GJ-021-BLA-L	8900210104300	1600.00	3290.00	t
301	21	1	5	AW-GJ-021-BLA-XL	8900210105301	1600.00	3290.00	t
302	21	1	6	AW-GJ-021-BLA-XXL	8900210106302	1600.00	3440.00	t
303	21	3	1	AW-GJ-021-NAV-XS	8900210301303	1600.00	3290.00	t
304	21	3	2	AW-GJ-021-NAV-S	8900210302304	1600.00	3290.00	t
305	21	3	3	AW-GJ-021-NAV-M	8900210303305	1600.00	3290.00	t
306	21	3	4	AW-GJ-021-NAV-L	8900210304306	1600.00	3290.00	t
307	21	3	5	AW-GJ-021-NAV-XL	8900210305307	1600.00	3290.00	t
308	21	3	6	AW-GJ-021-NAV-XXL	8900210306308	1600.00	3440.00	t
309	21	7	1	AW-GJ-021-CHA-XS	8900210701309	1600.00	3290.00	t
310	21	7	2	AW-GJ-021-CHA-S	8900210702310	1600.00	3290.00	t
311	21	7	3	AW-GJ-021-CHA-M	8900210703311	1600.00	3290.00	t
312	21	7	4	AW-GJ-021-CHA-L	8900210704312	1600.00	3290.00	t
313	21	7	5	AW-GJ-021-CHA-XL	8900210705313	1600.00	3290.00	t
314	21	7	6	AW-GJ-021-CHA-XXL	8900210706314	1600.00	3440.00	t
315	22	1	1	AW-CT-022-BLA-XS	8900220101315	1250.00	2690.00	t
316	22	1	2	AW-CT-022-BLA-S	8900220102316	1250.00	2690.00	t
317	22	1	3	AW-CT-022-BLA-M	8900220103317	1250.00	2690.00	t
318	22	1	4	AW-CT-022-BLA-L	8900220104318	1250.00	2690.00	t
319	22	1	5	AW-CT-022-BLA-XL	8900220105319	1250.00	2690.00	t
320	22	3	1	AW-CT-022-NAV-XS	8900220301320	1250.00	2690.00	t
321	22	3	2	AW-CT-022-NAV-S	8900220302321	1250.00	2690.00	t
322	22	3	3	AW-CT-022-NAV-M	8900220303322	1250.00	2690.00	t
323	22	3	4	AW-CT-022-NAV-L	8900220304323	1250.00	2690.00	t
324	22	3	5	AW-CT-022-NAV-XL	8900220305324	1250.00	2690.00	t
325	22	12	1	AW-CT-022-FOR-XS	8900221201325	1250.00	2890.00	t
326	22	12	2	AW-CT-022-FOR-S	8900221202326	1250.00	2890.00	t
327	22	12	3	AW-CT-022-FOR-M	8900221203327	1250.00	2890.00	t
328	22	12	4	AW-CT-022-FOR-L	8900221204328	1250.00	2890.00	t
329	22	12	5	AW-CT-022-FOR-XL	8900221205329	1250.00	2890.00	t
330	23	1	2	MS-TS-023-BLA-S	8900230102330	1050.00	2390.00	t
331	23	1	3	MS-TS-023-BLA-M	8900230103331	1050.00	2390.00	t
332	23	1	4	MS-TS-023-BLA-L	8900230104332	1050.00	2390.00	t
333	23	1	5	MS-TS-023-BLA-XL	8900230105333	1050.00	2390.00	t
334	23	5	2	MS-TS-023-OLI-S	8900230502334	1050.00	2390.00	t
335	23	5	3	MS-TS-023-OLI-M	8900230503335	1050.00	2390.00	t
336	23	5	4	MS-TS-023-OLI-L	8900230504336	1050.00	2390.00	t
337	24	1	8	MP-TR-024-BLA-30	8900240108337	1700.00	3490.00	t
338	24	1	9	MP-TR-024-BLA-32	8900240109338	1700.00	3490.00	t
339	24	1	10	MP-TR-024-BLA-34	8900240110339	1700.00	3490.00	t
340	24	1	11	MP-TR-024-BLA-36	8900240111340	1700.00	3490.00	t
341	24	6	9	MP-TR-024-BEI-32	8900240609341	1700.00	3490.00	t
342	24	6	10	MP-TR-024-BEI-34	8900240610342	1700.00	3490.00	t
343	24	6	11	MP-TR-024-BEI-36	8900240611343	1700.00	3490.00	t
344	24	8	8	MP-TR-024-GRE-30	8900240808344	1700.00	3490.00	t
345	24	8	9	MP-TR-024-GRE-32	8900240809345	1700.00	3490.00	t
346	24	8	10	MP-TR-024-GRE-34	8900240810346	1700.00	3490.00	t
347	24	8	11	MP-TR-024-GRE-36	8900240811347	1700.00	3490.00	t
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: clothing_store; Owner: postgres
--

COPY clothing_store.products (product_id, article_code, product_name, category_id, gender, brand, material, fit, season, base_cost_price, base_selling_price, product_status, availability_scope, description, search_tags) FROM stdin;
1	MS-FS-001	Regent Oxford Formal Shirt	2	MEN	North & Loom	100% Cotton	Slim	All Season	1850.00	3490.00	ACTIVE	ALL_BRANCHES	Crisp Oxford shirt for office and formal occasions.	["office", "formal", "professional", "cotton", "smart", "all-season"]
2	MS-CS-002	Harbor Linen Blend Shirt	3	MEN	North & Loom	55% Linen / 45% Cotton	Relaxed	Summer	2100.00	4190.00	ACTIVE	ALL_BRANCHES	Breathable linen-cotton shirt designed for warm weather and travel.	["summer", "travel", "comfortable", "breathable", "lightweight", "casual"]
3	MS-CS-003	Essential Cotton Button-Down	3	MEN	Daily Form	100% Cotton	Regular	All Season	1450.00	2890.00	ACTIVE	ALL_BRANCHES	Versatile cotton shirt for daily work and casual wear.	["cotton", "comfortable", "office", "casual", "everyday"]
4	MS-TS-004	City Grid Graphic T-Shirt	4	UNISEX	Streetline	Cotton Jersey	Oversized	Summer	850.00	1890.00	ACTIVE	ALL_BRANCHES	Oversized graphic T-shirt for street and weekend styling.	["casual", "streetwear", "oversized", "summer", "weekend"]
5	MS-TS-005	Core Crew Neck T-Shirt	4	MEN	Daily Form	Combed Cotton	Regular	All Season	680.00	1490.00	ACTIVE	ALL_BRANCHES	Soft everyday crew-neck T-shirt.	["basic", "comfortable", "cotton", "casual", "everyday"]
6	MS-PL-006	Heritage Pique Polo	5	MEN	North & Loom	Cotton Pique	Regular	Summer	1250.00	2690.00	ACTIVE	ALL_BRANCHES	Smart-casual polo suitable for office and weekend use.	["smart-casual", "office", "weekend", "summer", "cotton"]
7	MS-FS-007	Monarch Mandarin Collar Shirt	2	MEN	North & Loom	Cotton Satin	Regular	Festive	2050.00	3990.00	ACTIVE	ALL_BRANCHES	Mandarin-collar shirt for festive and semi-formal occasions.	["festive", "semi-formal", "smart", "cotton", "occasion"]
8	MS-CS-008	Breeze Short Sleeve Shirt	3	MEN	Daily Form	Lightweight Cotton	Relaxed	Summer	1250.00	2590.00	ACTIVE	ALL_BRANCHES	Lightweight short-sleeve shirt for hot days.	["summer", "breathable", "lightweight", "travel", "comfortable"]
9	MP-JN-009	Ridge Slim Fit Jeans	7	MEN	Denim Works	Stretch Denim	Slim	All Season	2350.00	4790.00	ACTIVE	ALL_BRANCHES	Slim jeans with light stretch for everyday movement.	["jeans", "denim", "casual", "stretch", "weekend"]
10	MP-JN-010	Foundry Straight Jeans	7	MEN	Denim Works	Rigid Denim	Straight	All Season	2500.00	4990.00	ACTIVE	ALL_BRANCHES	Straight-leg rigid denim jeans.	["jeans", "denim", "straight", "casual", "durable"]
11	MP-CP-011	Avenue Cotton Chinos	8	MEN	Daily Form	Cotton Twill	Tapered	All Season	1900.00	3890.00	ACTIVE	ALL_BRANCHES	Tapered cotton chinos for smart-casual dressing.	["chinos", "cotton", "smart-casual", "office", "comfortable"]
12	MP-TR-012	Executive Pleated Trousers	9	MEN	North & Loom	Poly-Viscose	Tailored	All Season	2250.00	4490.00	ACTIVE	ALL_BRANCHES	Tailored formal trousers with a clean pleated front.	["office", "formal", "professional", "tailored", "business"]
13	MP-TR-013	Comfort Stretch Trousers	9	MEN	Daily Form	Cotton Stretch Blend	Regular	All Season	1850.00	3790.00	ACTIVE	ALL_BRANCHES	Smart trousers with stretch for all-day comfort.	["office", "comfortable", "smart-casual", "stretch", "travel"]
14	MP-CG-014	Utility Six-Pocket Cargo	11	MEN	Streetline	Cotton Ripstop	Relaxed	All Season	2050.00	4290.00	ACTIVE	LHR_EXCLUSIVE	Relaxed utility cargo with six functional pockets.	["cargo", "utility", "casual", "travel", "durable"]
15	MP-SH-015	Weekend Denim Shorts	10	MEN	Denim Works	Stretch Denim	Regular	Summer	1550.00	3190.00	ACTIVE	ALL_BRANCHES	Comfortable denim shorts for casual summer wear.	["shorts", "denim", "summer", "weekend", "casual"]
16	MP-CP-016	Classic Cotton Pants	8	MEN	Daily Form	Cotton Twill	Straight	All Season	1750.00	3590.00	ACTIVE	ALL_BRANCHES	Straight cotton pants for office and daily use.	["cotton", "office", "comfortable", "everyday", "smart-casual"]
17	AW-GT-017	Velocity Training T-Shirt	13	UNISEX	Motion Lab	Moisture-Wicking Polyester	Athletic	All Season	1150.00	2490.00	ACTIVE	ALL_BRANCHES	Quick-dry training T-shirt for gym and running.	["gym", "activewear", "lightweight", "breathable", "training", "running"]
18	AW-GS-018	Motion Training Shorts	13	UNISEX	Motion Lab	Performance Knit	Athletic	Summer	1300.00	2790.00	ACTIVE	ALL_BRANCHES	Flexible gym shorts with quick-dry fabric.	["gym", "activewear", "shorts", "lightweight", "training"]
19	AW-TP-019	Sprint Tapered Track Pants	14	UNISEX	Motion Lab	Interlock Polyester	Tapered	All Season	1750.00	3590.00	ACTIVE	ALL_BRANCHES	Tapered track pants for training and travel.	["gym", "track-pants", "travel", "comfortable", "training"]
20	AW-HD-020	Metro Fleece Hoodie	15	UNISEX	Streetline	Cotton Fleece	Relaxed	Winter	2250.00	4690.00	ACTIVE	ISB_EXCLUSIVE	Warm relaxed hoodie for winter and casual wear.	["winter", "hoodie", "warm", "comfortable", "casual"]
21	AW-GJ-021	Aero Gym Joggers	13	UNISEX	Motion Lab	Stretch Performance Knit	Tapered	All Season	1600.00	3290.00	ACTIVE	ALL_BRANCHES	Stretch joggers for training and daily comfort.	["gym", "joggers", "stretch", "comfortable", "activewear"]
22	AW-CT-022	Flex Compression Tee	13	UNISEX	Motion Lab	Compression Polyester	Compression	All Season	1250.00	2690.00	ACTIVE	ALL_BRANCHES	Compression training top for high-intensity workouts.	["gym", "compression", "training", "performance", "activewear"]
23	MS-TS-023	Limited Drop Neon Tee	4	UNISEX	Streetline	Cotton Jersey	Oversized	Summer	1050.00	2390.00	ACTIVE	LHR_EXCLUSIVE	Limited oversized graphic T-shirt.	["limited", "streetwear", "oversized", "summer", "casual"]
24	MP-TR-024	Studio Drawstring Trousers	9	MEN	Daily Form	Cotton Blend	Relaxed	All Season	1700.00	3490.00	ACTIVE	KHI_EXCLUSIVE	Relaxed drawstring trousers for travel and casual office wear.	["comfortable", "travel", "smart-casual", "relaxed", "office"]
\.


--
-- Data for Name: sizes; Type: TABLE DATA; Schema: clothing_store; Owner: postgres
--

COPY clothing_store.sizes (size_id, size_label, size_type, sort_order) FROM stdin;
1	XS	ALPHA	1
2	S	ALPHA	2
3	M	ALPHA	3
4	L	ALPHA	4
5	XL	ALPHA	5
6	XXL	ALPHA	6
7	28	WAIST	10
8	30	WAIST	11
9	32	WAIST	12
10	34	WAIST	13
11	36	WAIST	14
12	38	WAIST	15
\.


--
-- Name: branch_inventory_inventory_id_seq; Type: SEQUENCE SET; Schema: clothing_store; Owner: postgres
--

SELECT pg_catalog.setval('clothing_store.branch_inventory_inventory_id_seq', 784, true);


--
-- Name: branches_branch_id_seq; Type: SEQUENCE SET; Schema: clothing_store; Owner: postgres
--

SELECT pg_catalog.setval('clothing_store.branches_branch_id_seq', 3, true);


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: clothing_store; Owner: postgres
--

SELECT pg_catalog.setval('clothing_store.categories_category_id_seq', 15, true);


--
-- Name: colors_color_id_seq; Type: SEQUENCE SET; Schema: clothing_store; Owner: postgres
--

SELECT pg_catalog.setval('clothing_store.colors_color_id_seq', 44, true);


--
-- Name: product_images_image_id_seq; Type: SEQUENCE SET; Schema: clothing_store; Owner: postgres
--

SELECT pg_catalog.setval('clothing_store.product_images_image_id_seq', 127, true);


--
-- Name: product_variants_variant_id_seq; Type: SEQUENCE SET; Schema: clothing_store; Owner: postgres
--

SELECT pg_catalog.setval('clothing_store.product_variants_variant_id_seq', 347, true);


--
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: clothing_store; Owner: postgres
--

SELECT pg_catalog.setval('clothing_store.products_product_id_seq', 24, true);


--
-- Name: sizes_size_id_seq; Type: SEQUENCE SET; Schema: clothing_store; Owner: postgres
--

SELECT pg_catalog.setval('clothing_store.sizes_size_id_seq', 12, true);


--
-- Name: cart_items cart_items_cart_id_variant_id_branch_id_key; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.cart_items
    ADD CONSTRAINT cart_items_cart_id_variant_id_branch_id_key UNIQUE (cart_id, variant_id, branch_id);


--
-- Name: cart_items cart_items_pkey; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.cart_items
    ADD CONSTRAINT cart_items_pkey PRIMARY KEY (cart_item_id);


--
-- Name: carts carts_pkey; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.carts
    ADD CONSTRAINT carts_pkey PRIMARY KEY (cart_id);


--
-- Name: conversation_messages conversation_messages_pkey; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.conversation_messages
    ADD CONSTRAINT conversation_messages_pkey PRIMARY KEY (message_id);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (conversation_id);


--
-- Name: displayed_results displayed_results_pkey; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.displayed_results
    ADD CONSTRAINT displayed_results_pkey PRIMARY KEY (displayed_result_id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (order_item_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: stock_reservations stock_reservations_pkey; Type: CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.stock_reservations
    ADD CONSTRAINT stock_reservations_pkey PRIMARY KEY (reservation_id);


--
-- Name: branch_inventory branch_inventory_branch_id_variant_id_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.branch_inventory
    ADD CONSTRAINT branch_inventory_branch_id_variant_id_key UNIQUE (branch_id, variant_id);


--
-- Name: branch_inventory branch_inventory_pkey; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.branch_inventory
    ADD CONSTRAINT branch_inventory_pkey PRIMARY KEY (inventory_id);


--
-- Name: branches branches_branch_code_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.branches
    ADD CONSTRAINT branches_branch_code_key UNIQUE (branch_code);


--
-- Name: branches branches_pkey; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.branches
    ADD CONSTRAINT branches_pkey PRIMARY KEY (branch_id);


--
-- Name: categories categories_category_code_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.categories
    ADD CONSTRAINT categories_category_code_key UNIQUE (category_code);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: colors colors_color_code_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.colors
    ADD CONSTRAINT colors_color_code_key UNIQUE (color_code);


--
-- Name: colors colors_color_name_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.colors
    ADD CONSTRAINT colors_color_name_key UNIQUE (color_name);


--
-- Name: colors colors_pkey; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.colors
    ADD CONSTRAINT colors_pkey PRIMARY KEY (color_id);


--
-- Name: product_images product_images_pkey; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_images
    ADD CONSTRAINT product_images_pkey PRIMARY KEY (image_id);


--
-- Name: product_variants product_variants_barcode_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_variants
    ADD CONSTRAINT product_variants_barcode_key UNIQUE (barcode);


--
-- Name: product_variants product_variants_pkey; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_variants
    ADD CONSTRAINT product_variants_pkey PRIMARY KEY (variant_id);


--
-- Name: product_variants product_variants_product_id_color_id_size_id_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_variants
    ADD CONSTRAINT product_variants_product_id_color_id_size_id_key UNIQUE (product_id, color_id, size_id);


--
-- Name: product_variants product_variants_sku_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_variants
    ADD CONSTRAINT product_variants_sku_key UNIQUE (sku);


--
-- Name: products products_article_code_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.products
    ADD CONSTRAINT products_article_code_key UNIQUE (article_code);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: sizes sizes_pkey; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.sizes
    ADD CONSTRAINT sizes_pkey PRIMARY KEY (size_id);


--
-- Name: sizes sizes_size_label_size_type_key; Type: CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.sizes
    ADD CONSTRAINT sizes_size_label_size_type_key UNIQUE (size_label, size_type);


--
-- Name: idx_carts_session_status; Type: INDEX; Schema: agent_runtime; Owner: postgres
--

CREATE INDEX idx_carts_session_status ON agent_runtime.carts USING btree (session_id, status);


--
-- Name: idx_conversations_session; Type: INDEX; Schema: agent_runtime; Owner: postgres
--

CREATE INDEX idx_conversations_session ON agent_runtime.conversations USING btree (session_id);


--
-- Name: idx_displayed_results_lookup; Type: INDEX; Schema: agent_runtime; Owner: postgres
--

CREATE INDEX idx_displayed_results_lookup ON agent_runtime.displayed_results USING btree (conversation_id, "position", created_at);


--
-- Name: idx_messages_conversation; Type: INDEX; Schema: agent_runtime; Owner: postgres
--

CREATE INDEX idx_messages_conversation ON agent_runtime.conversation_messages USING btree (conversation_id, created_at);


--
-- Name: idx_orders_session_status; Type: INDEX; Schema: agent_runtime; Owner: postgres
--

CREATE INDEX idx_orders_session_status ON agent_runtime.orders USING btree (session_id, status);


--
-- Name: idx_reservations_variant_branch; Type: INDEX; Schema: agent_runtime; Owner: postgres
--

CREATE INDEX idx_reservations_variant_branch ON agent_runtime.stock_reservations USING btree (variant_id, branch_id, status);


--
-- Name: idx_inventory_branch; Type: INDEX; Schema: clothing_store; Owner: postgres
--

CREATE INDEX idx_inventory_branch ON clothing_store.branch_inventory USING btree (branch_id);


--
-- Name: idx_inventory_variant; Type: INDEX; Schema: clothing_store; Owner: postgres
--

CREATE INDEX idx_inventory_variant ON clothing_store.branch_inventory USING btree (variant_id);


--
-- Name: idx_products_category; Type: INDEX; Schema: clothing_store; Owner: postgres
--

CREATE INDEX idx_products_category ON clothing_store.products USING btree (category_id);


--
-- Name: idx_products_name; Type: INDEX; Schema: clothing_store; Owner: postgres
--

CREATE INDEX idx_products_name ON clothing_store.products USING btree (product_name);


--
-- Name: idx_products_tags_gin; Type: INDEX; Schema: clothing_store; Owner: postgres
--

CREATE INDEX idx_products_tags_gin ON clothing_store.products USING gin (search_tags);


--
-- Name: idx_variants_product; Type: INDEX; Schema: clothing_store; Owner: postgres
--

CREATE INDEX idx_variants_product ON clothing_store.product_variants USING btree (product_id);


--
-- Name: cart_items cart_items_branch_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.cart_items
    ADD CONSTRAINT cart_items_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES clothing_store.branches(branch_id);


--
-- Name: cart_items cart_items_cart_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.cart_items
    ADD CONSTRAINT cart_items_cart_id_fkey FOREIGN KEY (cart_id) REFERENCES agent_runtime.carts(cart_id) ON DELETE CASCADE;


--
-- Name: cart_items cart_items_product_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.cart_items
    ADD CONSTRAINT cart_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES clothing_store.products(product_id);


--
-- Name: cart_items cart_items_variant_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.cart_items
    ADD CONSTRAINT cart_items_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES clothing_store.product_variants(variant_id);


--
-- Name: conversation_messages conversation_messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.conversation_messages
    ADD CONSTRAINT conversation_messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES agent_runtime.conversations(conversation_id) ON DELETE CASCADE;


--
-- Name: displayed_results displayed_results_branch_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.displayed_results
    ADD CONSTRAINT displayed_results_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES clothing_store.branches(branch_id);


--
-- Name: displayed_results displayed_results_conversation_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.displayed_results
    ADD CONSTRAINT displayed_results_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES agent_runtime.conversations(conversation_id) ON DELETE CASCADE;


--
-- Name: displayed_results displayed_results_message_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.displayed_results
    ADD CONSTRAINT displayed_results_message_id_fkey FOREIGN KEY (message_id) REFERENCES agent_runtime.conversation_messages(message_id) ON DELETE CASCADE;


--
-- Name: displayed_results displayed_results_product_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.displayed_results
    ADD CONSTRAINT displayed_results_product_id_fkey FOREIGN KEY (product_id) REFERENCES clothing_store.products(product_id);


--
-- Name: displayed_results displayed_results_variant_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.displayed_results
    ADD CONSTRAINT displayed_results_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES clothing_store.product_variants(variant_id);


--
-- Name: order_items order_items_branch_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.order_items
    ADD CONSTRAINT order_items_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES clothing_store.branches(branch_id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES agent_runtime.orders(order_id) ON DELETE CASCADE;


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES clothing_store.products(product_id);


--
-- Name: order_items order_items_variant_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.order_items
    ADD CONSTRAINT order_items_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES clothing_store.product_variants(variant_id);


--
-- Name: orders orders_cart_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.orders
    ADD CONSTRAINT orders_cart_id_fkey FOREIGN KEY (cart_id) REFERENCES agent_runtime.carts(cart_id);


--
-- Name: stock_reservations stock_reservations_branch_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.stock_reservations
    ADD CONSTRAINT stock_reservations_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES clothing_store.branches(branch_id);


--
-- Name: stock_reservations stock_reservations_order_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.stock_reservations
    ADD CONSTRAINT stock_reservations_order_id_fkey FOREIGN KEY (order_id) REFERENCES agent_runtime.orders(order_id) ON DELETE CASCADE;


--
-- Name: stock_reservations stock_reservations_variant_id_fkey; Type: FK CONSTRAINT; Schema: agent_runtime; Owner: postgres
--

ALTER TABLE ONLY agent_runtime.stock_reservations
    ADD CONSTRAINT stock_reservations_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES clothing_store.product_variants(variant_id);


--
-- Name: branch_inventory branch_inventory_branch_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.branch_inventory
    ADD CONSTRAINT branch_inventory_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES clothing_store.branches(branch_id);


--
-- Name: branch_inventory branch_inventory_variant_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.branch_inventory
    ADD CONSTRAINT branch_inventory_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES clothing_store.product_variants(variant_id);


--
-- Name: categories categories_parent_category_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.categories
    ADD CONSTRAINT categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES clothing_store.categories(category_id);


--
-- Name: product_images product_images_color_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_images
    ADD CONSTRAINT product_images_color_id_fkey FOREIGN KEY (color_id) REFERENCES clothing_store.colors(color_id) ON DELETE CASCADE;


--
-- Name: product_images product_images_product_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_images
    ADD CONSTRAINT product_images_product_id_fkey FOREIGN KEY (product_id) REFERENCES clothing_store.products(product_id) ON DELETE CASCADE;


--
-- Name: product_variants product_variants_color_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_variants
    ADD CONSTRAINT product_variants_color_id_fkey FOREIGN KEY (color_id) REFERENCES clothing_store.colors(color_id);


--
-- Name: product_variants product_variants_product_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_variants
    ADD CONSTRAINT product_variants_product_id_fkey FOREIGN KEY (product_id) REFERENCES clothing_store.products(product_id);


--
-- Name: product_variants product_variants_size_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.product_variants
    ADD CONSTRAINT product_variants_size_id_fkey FOREIGN KEY (size_id) REFERENCES clothing_store.sizes(size_id);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: clothing_store; Owner: postgres
--

ALTER TABLE ONLY clothing_store.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES clothing_store.categories(category_id);


--
-- PostgreSQL database dump complete
--

\unrestrict BL7CqmGhNfHWdHPaP2XXlmIecnvSlFRTmYvy7A3cePATptQm2hKt0CvZriqJzKf
