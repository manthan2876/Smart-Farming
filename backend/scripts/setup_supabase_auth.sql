-- ==============================================================================
-- SMART FARMING: SUPABASE AUTHENTICATION INTEGRATION TRIGGER
-- ==============================================================================
-- 1. Ensure password_hash in public.users is nullable (since Supabase manages auth.users)
ALTER TABLE public.users ALTER COLUMN password_hash DROP NOT NULL;

-- 2. Define trigger function to sync auth.users into public.users and provision public.farms
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
  v_role text;
  v_name text;
  v_language text;
  v_farm_name text;
  v_location text;
BEGIN
  v_role := coalesce(new.raw_user_meta_data->>'role', 'farmer');
  v_name := coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1));
  v_language := coalesce(new.raw_user_meta_data->>'language', 'English');
  v_location := coalesce(new.raw_user_meta_data->>'location', 'Gujarat, India');
  v_farm_name := coalesce(new.raw_user_meta_data->>'farm_name', (v_name || '''s Farm'));

  -- Insert or update public.users
  INSERT INTO public.users (
    id,
    email,
    phone,
    name,
    language,
    role,
    created_at
  )
  VALUES (
    new.id::text,
    new.email,
    new.phone,
    v_name,
    v_language,
    v_role,
    coalesce(new.created_at, now())
  )
  ON CONFLICT (id) DO UPDATE SET
    email = excluded.email,
    phone = coalesce(excluded.phone, public.users.phone),
    name = coalesce(excluded.name, public.users.name),
    role = coalesce(excluded.role, public.users.role);

  -- If user role is farmer, automatically create their initial Farm record if not present
  IF v_role = 'farmer' THEN
    INSERT INTO public.farms (
      user_id,
      name,
      location,
      area_acres,
      latitude,
      longitude,
      crop_history
    )
    VALUES (
      new.id::text,
      v_farm_name,
      v_location,
      nullif(new.raw_user_meta_data->>'farm_area_acres', '')::double precision,
      nullif(new.raw_user_meta_data->>'latitude', '')::double precision,
      nullif(new.raw_user_meta_data->>'longitude', '')::double precision,
      '[]'::json
    )
    ON CONFLICT (user_id) DO NOTHING;
  END IF;

  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Install the trigger on auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT OR UPDATE ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

