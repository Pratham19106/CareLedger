const pool = require('../src/config/db');

const sql = `
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_policies
    WHERE schemaname = 'storage'
      AND tablename = 'objects'
      AND policyname = 'clinic logos anon insert doctor folder'
  ) THEN
    CREATE POLICY "clinic logos anon insert doctor folder"
    ON storage.objects
    FOR INSERT
    TO anon
    WITH CHECK (
      bucket_id = 'clinic-logos'
      AND (storage.foldername(name))[1] = 'doctor-clinics'
    );
  END IF;
END
$$;
`;

(async () => {
    try {
        await pool.query(sql);
        console.log('Policy ensured: clinic logos anon insert doctor folder');
    } catch (error) {
        console.error('Failed to apply policy:', error.message);
        process.exitCode = 1;
    } finally {
        await pool.end();
    }
})();
