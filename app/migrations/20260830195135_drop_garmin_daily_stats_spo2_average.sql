-- +goose Up
ALTER TABLE public."GarminDailyStats" DROP COLUMN "Spo2Average";

-- +goose Down
ALTER TABLE public."GarminDailyStats" ADD COLUMN "Spo2Average" INTEGER;
