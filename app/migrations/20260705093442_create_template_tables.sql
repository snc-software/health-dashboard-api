-- +goose Up
CREATE TABLE IF NOT EXISTS public."Templates" (
    "Id" UUID PRIMARY KEY,
    "Name" VARCHAR(200) NOT NULL,
    "CreatedTimestamp" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "UpdatedTimestamp" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "Deleted" BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS "IX_Templates_CreatedTimestamp_Id_Live"
    ON public."Templates" ("CreatedTimestamp" DESC, "Id")
    WHERE "Deleted" = FALSE;

-- +goose Down
DROP INDEX IF EXISTS public."IX_Templates_CreatedTimestamp_Id_Live";
DROP TABLE IF EXISTS public."Templates";
