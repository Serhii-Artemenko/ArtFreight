BEGIN;

CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    password_hash TEXT,

    role TEXT NOT NULL DEFAULT 'staff'
        CHECK (role IN ('staff', 'admin')),

    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Prevent duplicate accounts differing only by email capitalization.
CREATE UNIQUE INDEX users_email_unique
    ON users (LOWER(email));


CREATE TABLE do_drafts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    owner_id BIGINT NOT NULL
        REFERENCES users(id),

    template_id TEXT NOT NULL DEFAULT 'air_do',

    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'finalized')),

    sources JSONB NOT NULL,
    extraction JSONB NOT NULL,
    validation JSONB NOT NULL,
    form_values JSONB NOT NULL,
    field_statuses JSONB NOT NULL,

    revision INTEGER NOT NULL DEFAULT 1
        CHECK (revision >= 1),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finalized_at TIMESTAMPTZ,

    CHECK (
        (status = 'draft' AND finalized_at IS NULL)
        OR
        (status = 'finalized' AND finalized_at IS NOT NULL)
    )
);

-- Helps retrieve one user's D.O. history, newest first.
CREATE INDEX do_drafts_owner_created
    ON do_drafts (owner_id, created_at DESC);

COMMIT;