-- Add clinic reference to consultations so clinic details are tied to the exact consultation.
ALTER TABLE public.consultations
ADD COLUMN IF NOT EXISTS clinic_id uuid;

ALTER TABLE public.consultations
DROP CONSTRAINT IF EXISTS consultations_clinic_id_fkey;

ALTER TABLE public.consultations
ADD CONSTRAINT consultations_clinic_id_fkey
FOREIGN KEY (clinic_id) REFERENCES public.clinics(id);

CREATE INDEX IF NOT EXISTS idx_consultations_clinic_id
ON public.consultations(clinic_id);
