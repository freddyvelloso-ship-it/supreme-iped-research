-- SUPREME V4 - session event contract
--
-- The launcher records forensic work-session boundaries after the psychometric
-- pre-gate and after IPED closes. These are operational custody events, not
-- psychometric submissions. The API model accepts them; the database CHECK must
-- accept them too for existing local/staging/prod databases.

ALTER TABLE events_raw
  DROP CONSTRAINT IF EXISTS events_raw_event_type_check;

ALTER TABLE events_raw
  ADD CONSTRAINT events_raw_event_type_check
  CHECK (event_type IN (
    'file_open',
    'image_view',
    'video_play',
    'classification_event',
    'session_start',
    'session_end'
  ));
