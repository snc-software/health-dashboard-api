-- +goose Up
CREATE TABLE IF NOT EXISTS public."StravaActivities" (
    "Id" UUID PRIMARY KEY,
    "StravaActivityId" BIGINT NOT NULL,
    "Name" TEXT NOT NULL,
    "Type" TEXT NOT NULL,
    "SportType" TEXT NOT NULL,
    "StartDate" TIMESTAMPTZ NOT NULL,
    "StartDateLocal" TIMESTAMPTZ NOT NULL,
    "DistanceMetres" DOUBLE PRECISION NOT NULL,
    "MovingTimeSeconds" INTEGER NOT NULL,
    "ElapsedTimeSeconds" INTEGER NOT NULL,
    "TotalElevationGainMetres" DOUBLE PRECISION NOT NULL,
    "AverageHeartrate" DOUBLE PRECISION,
    "MaxHeartrate" DOUBLE PRECISION,
    "GearId" TEXT,
    "UpdatedTimestamp" TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS "UX_StravaActivities_StravaActivityId"
    ON public."StravaActivities" ("StravaActivityId");

-- +goose Down
DROP INDEX IF EXISTS public."UX_StravaActivities_StravaActivityId";
DROP TABLE IF EXISTS public."StravaActivities";
