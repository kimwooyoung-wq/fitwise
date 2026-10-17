-- CI-only compatibility shim for Supabase Auth. Never deploy this file.
create schema if not exists auth;
create table if not exists auth.users (id uuid primary key);
create or replace function auth.uid() returns uuid
language sql stable
as $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
do $$ begin
    create role anon nologin;
exception when duplicate_object then null;
end $$;
do $$ begin
    create role authenticated nologin;
exception when duplicate_object then null;
end $$;
grant usage on schema auth to authenticated;
grant execute on function auth.uid() to authenticated;
