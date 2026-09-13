// GDR public frontend configuration.
// Safe to expose only the Supabase PROJECT URL and PUBLISHABLE key in browser code
// when Row Level Security (RLS) is correctly configured.
// NEVER place a Supabase service_role key, Resend API key, admin password, or other secret here.
window.GDR_CONFIG = {
  supabaseUrl: 'https://klwzkmfzxrikqslkclik.supabase.co',
  supabasePublishableKey: 'sb_publishable_PeoU1Z8jnXXptuck9Zb_Jg_QEeBLZKm',
  backendEnabled: true,
  siteUrl: 'https://www.gdrnetwork.org/',
  appBasePath: '/gdr/',
  emailFunctionName: 'send-gdr-email',
  productionDomain: 'www.gdrnetwork.org'
};
