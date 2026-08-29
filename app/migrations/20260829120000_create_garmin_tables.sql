-- +goose Up
CREATE TABLE IF NOT EXISTS public."GarminTokens" (
    "Id" UUID PRIMARY KEY,
    "TokenData" TEXT NOT NULL,
    "CreatedTimestamp" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "UpdatedTimestamp" TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public."GarminDailyStats" (
    "Id" UUID PRIMARY KEY,
    "StatDate" DATE NOT NULL,
    "Steps" INTEGER,
    "RestingHeartRate" INTEGER,
    "SleepSeconds" INTEGER,
    "BodyBattery" INTEGER,
    "UpdatedTimestamp" TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS "UX_GarminDailyStats_StatDate"
    ON public."GarminDailyStats" ("StatDate");

-- +goose Down
DROP INDEX IF EXISTS public."UX_GarminDailyStats_StatDate";
DROP TABLE IF EXISTS public."GarminDailyStats";
DROP TABLE IF EXISTS public."GarminTokens";
