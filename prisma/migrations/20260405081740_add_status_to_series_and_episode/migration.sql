/*
  Warnings:

  - You are about to drop the column `videoFile` on the `episodes` table. All the data in the column will be lost.

*/
-- CreateEnum
CREATE TYPE "SeriesStatus" AS ENUM ('DRAFT', 'PUBLISHED');

-- AlterTable
ALTER TABLE "episodes" DROP COLUMN "videoFile",
ADD COLUMN     "duration" DOUBLE PRECISION,
ADD COLUMN     "isProcessing" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "muxAssetId" TEXT,
ADD COLUMN     "muxPlaybackId" TEXT,
ADD COLUMN     "status" "SeriesStatus" NOT NULL DEFAULT 'DRAFT',
ALTER COLUMN "resolution" SET DEFAULT '1080p';

-- AlterTable
ALTER TABLE "series" ADD COLUMN     "status" "SeriesStatus" NOT NULL DEFAULT 'DRAFT',
ADD COLUMN     "totalViewers" INTEGER NOT NULL DEFAULT 0;

-- CreateTable
CREATE TABLE "saved_episodes" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "episodeId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "saved_episodes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ratings" (
    "id" TEXT NOT NULL,
    "userName" TEXT NOT NULL,
    "userImage" TEXT,
    "stars" DOUBLE PRECISION NOT NULL,
    "feedback" TEXT NOT NULL,
    "seriesId" TEXT NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ratings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "episode_views" (
    "id" TEXT NOT NULL,
    "episodeId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "episode_views_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "saved_episodes_userId_episodeId_key" ON "saved_episodes"("userId", "episodeId");

-- AddForeignKey
ALTER TABLE "saved_episodes" ADD CONSTRAINT "saved_episodes_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "saved_episodes" ADD CONSTRAINT "saved_episodes_episodeId_fkey" FOREIGN KEY ("episodeId") REFERENCES "episodes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ratings" ADD CONSTRAINT "ratings_seriesId_fkey" FOREIGN KEY ("seriesId") REFERENCES "series"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "episode_views" ADD CONSTRAINT "episode_views_episodeId_fkey" FOREIGN KEY ("episodeId") REFERENCES "episodes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "episode_views" ADD CONSTRAINT "episode_views_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
