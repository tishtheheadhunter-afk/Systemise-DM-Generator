-- Run this in Supabase SQL Editor to create the table for thread persistence

CREATE TABLE IF NOT EXISTS bdc_dm_threads (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    context TEXT,
    messages JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups by updated_at (for sorting recent threads)
CREATE INDEX IF NOT EXISTS idx_bdc_dm_threads_updated_at 
ON bdc_dm_threads(updated_at DESC);

-- Trigger to auto-update updated_at on any UPDATE
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_bdc_dm_threads_updated_at ON bdc_dm_threads;
CREATE TRIGGER update_bdc_dm_threads_updated_at
    BEFORE UPDATE ON bdc_dm_threads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (optional but recommended)
ALTER TABLE bdc_dm_threads ENABLE ROW LEVEL SECURITY;

-- Permissive policy for the anon key (suitable for an internal team tool)
DROP POLICY IF EXISTS "Allow all operations" ON bdc_dm_threads;
CREATE POLICY "Allow all operations" ON bdc_dm_threads
    FOR ALL
    USING (true)
    WITH CHECK (true);
