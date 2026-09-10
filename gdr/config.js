// GDR public frontend configuration.
// Safe to keep the Supabase PROJECT URL and PUBLISHABLE/ANON key in a browser app
// only when Row Level Security (RLS) is correctly configured.
// NEVER place a Supabase service_role key in this file or anywhere in GitHub Pages.
window.GDR_CONFIG = {
  supabaseUrl: '',
  supabasePublishableKey: '',
  backendEnabled: false,
  siteUrl: 'https://dataprofessor-faheem.github.io/gdr/'
};
