CREATE TABLE IF NOT EXISTS resources (
    resource_id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    short_description TEXT NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    effort_level VARCHAR(100) NOT NULL,
    practicality_level VARCHAR(200) NOT NULL,
    language VARCHAR(20) NOT NULL,
    topic_area VARCHAR(200) NOT NULL,
    recommended_rank INTEGER NULL,
    featured_m6 BOOLEAN NOT NULL DEFAULT FALSE,
    quality_note TEXT NOT NULL,
    source_owner_org TEXT NOT NULL,
    source_year_or_last_update VARCHAR(20) NOT NULL,
    access_conditions VARCHAR(100) NOT NULL,
    contributor_partner VARCHAR(200) NOT NULL,
    review_status VARCHAR(100) NOT NULL,
    review_due_date DATE NOT NULL,
    last_checked_date DATE NOT NULL,
    editor_notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS audiences (
    code VARCHAR(100) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS tasks (
    code VARCHAR(20) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS stages (
    code VARCHAR(100) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS personas (
    code VARCHAR(100) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS resource_audiences (
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    audience_code VARCHAR(100) NOT NULL REFERENCES audiences(code),
    PRIMARY KEY (resource_id, audience_code)
);

CREATE TABLE IF NOT EXISTS resource_tasks (
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    task_code VARCHAR(20) NOT NULL REFERENCES tasks(code),
    PRIMARY KEY (resource_id, task_code)
);

CREATE TABLE IF NOT EXISTS resource_stages (
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    stage_code VARCHAR(100) NOT NULL REFERENCES stages(code),
    PRIMARY KEY (resource_id, stage_code)
);

CREATE TABLE IF NOT EXISTS resource_personas (
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    persona_code VARCHAR(100) NOT NULL REFERENCES personas(code),
    PRIMARY KEY (resource_id, persona_code)
);

CREATE TABLE IF NOT EXISTS resource_keywords (
    resource_id VARCHAR(50) NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    keyword_id INTEGER NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    PRIMARY KEY (resource_id, keyword_id)
);

CREATE INDEX IF NOT EXISTS idx_resources_resource_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_featured_m6 ON resources(featured_m6);
CREATE INDEX IF NOT EXISTS idx_resources_review_status ON resources(review_status);

CREATE INDEX IF NOT EXISTS idx_resource_audiences_audience ON resource_audiences(audience_code);
CREATE INDEX IF NOT EXISTS idx_resource_tasks_task ON resource_tasks(task_code);
CREATE INDEX IF NOT EXISTS idx_resource_stages_stage ON resource_stages(stage_code);
CREATE INDEX IF NOT EXISTS idx_resource_personas_persona ON resource_personas(persona_code);
CREATE INDEX IF NOT EXISTS idx_resource_keywords_keyword ON resource_keywords(keyword_id);

INSERT INTO audiences (code) VALUES
('DMO'),
('SME'),
('Public authority'),
('Data/tech provider')
ON CONFLICT DO NOTHING;

INSERT INTO tasks (code) VALUES
('T1'), ('T2'), ('T3'), ('T4'), ('T5')
ON CONFLICT DO NOTHING;

INSERT INTO stages (code) VALUES
('Explore'),
('Prepare'),
('Pilot'),
('Scale')
ON CONFLICT DO NOTHING;

INSERT INTO personas (code) VALUES
('DMO'),
('SME'),
('Public authority'),
('Tech provider')
ON CONFLICT DO NOTHING;

INSERT INTO resources (
    resource_id,
    title,
    url,
    short_description,
    resource_type,
    effort_level,
    practicality_level,
    language,
    topic_area,
    recommended_rank,
    featured_m6,
    quality_note,
    source_owner_org,
    source_year_or_last_update,
    access_conditions,
    contributor_partner,
    review_status,
    review_due_date,
    last_checked_date,
    editor_notes
) VALUES (
    'FAC-R-0001',
    'Blueprint and Roadmap for Deploying the European Tourism Data Space (ETDS) - Final Draft 3.0 (Dec 2023)',
    'https://www.tourismdataspace-csa.eu/',
    'Entry-point reference for the European Tourism Data Space (ETDS). Explains governance, legal/regulatory context, technical specifications, business models, minimum viable data space use cases, and an ETDS deployment roadmap with links to deeper resources.',
    'Blueprint',
    'deep dive',
    'Background (with strong Implementation pointers via links)',
    'EN',
    'Interoperability',
    1,
    TRUE,
    'Comprehensive umbrella reference; not intended as an exhaustive technical manual-use linked resources for deeper technical detail.',
    'DATES Tourism Consortium Partners / Data Space for Tourism Consortium Partners',
    '2023-12',
    'Open',
    'DIHT4.0',
    'Proposed',
    DATE '2026-12-31',
    CURRENT_DATE,
    ''
) ON CONFLICT (resource_id) DO NOTHING;

INSERT INTO keywords (keyword) VALUES
('etds'),
('d3hub'),
('governance'),
('interoperability'),
('standards'),
('dcat_ap'),
('odrl'),
('ids_gaiax'),
('use_cases'),
('business_models')
ON CONFLICT DO NOTHING;

INSERT INTO resource_audiences (resource_id, audience_code) VALUES
('FAC-R-0001', 'DMO'),
('FAC-R-0001', 'SME'),
('FAC-R-0001', 'Public authority'),
('FAC-R-0001', 'Data/tech provider')
ON CONFLICT DO NOTHING;

INSERT INTO resource_tasks (resource_id, task_code) VALUES
('FAC-R-0001', 'T1'),
('FAC-R-0001', 'T2'),
('FAC-R-0001', 'T3'),
('FAC-R-0001', 'T4'),
('FAC-R-0001', 'T5')
ON CONFLICT DO NOTHING;

INSERT INTO resource_stages (resource_id, stage_code) VALUES
('FAC-R-0001', 'Explore'),
('FAC-R-0001', 'Prepare'),
('FAC-R-0001', 'Pilot')
ON CONFLICT DO NOTHING;

INSERT INTO resource_personas (resource_id, persona_code) VALUES
('FAC-R-0001', 'DMO'),
('FAC-R-0001', 'SME'),
('FAC-R-0001', 'Public authority'),
('FAC-R-0001', 'Tech provider')
ON CONFLICT DO NOTHING;

INSERT INTO resource_keywords (resource_id, keyword_id)
SELECT 'FAC-R-0001', k.id
FROM keywords k
WHERE k.keyword IN ('etds', 'd3hub', 'governance', 'interoperability', 'standards', 'dcat_ap', 'odrl', 'ids_gaiax', 'use_cases', 'business_models')
ON CONFLICT DO NOTHING;
