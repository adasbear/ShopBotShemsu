-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS referrals (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  referrer_id BIGINT NOT NULL,
  referred_id BIGINT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS referral_earnings (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  referrer_id BIGINT NOT NULL,
  referred_id BIGINT NOT NULL,
  order_group TEXT NOT NULL,
  items TEXT,
  earned_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_id);
CREATE INDEX IF NOT EXISTS idx_referral_earnings_referrer ON referral_earnings(referrer_id);
