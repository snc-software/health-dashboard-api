-- +goose Up
CREATE TABLE IF NOT EXISTS public."StravaTokens" (
    "Id" UUID PRIMARY KEY,
    "AccessToken" TEXT NOT NULL,
    "RefreshToken" TEXT NOT NULL,
    "ExpiresAt" TIMESTAMPTZ NOT NULL,
    "AthleteId" BIGINT NOT NULL,
    "Scope" TEXT NOT NULL,
    "CreatedTimestamp" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "UpdatedTimestamp" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- +goose Down
DROP TABLE IF EXISTS public."StravaTokens";
