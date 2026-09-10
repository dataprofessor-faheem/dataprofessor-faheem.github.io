// GDR shared-backend bridge. Works in fallback mode until config.js is populated.
window.GDRBackend = (() => {
  let client = null;
  const config = () => window.GDR_CONFIG || {};

  async function ensureClient() {
    const c = config();
    if (!c.backendEnabled || !c.supabaseUrl || !c.supabasePublishableKey || !window.supabase) return null;
    if (!client) client = window.supabase.createClient(c.supabaseUrl, c.supabasePublishableKey);
    return client;
  }

  async function getSession() {
    const c = await ensureClient();
    if (!c) return { mode: 'local', session: null };
    const { data, error } = await c.auth.getSession();
    if (error) throw error;
    return { mode: 'shared', session: data.session };
  }

  async function signUp(email, password) {
    const c = await ensureClient();
    if (!c) throw new Error('Shared backend is not configured yet.');
    return c.auth.signUp({ email, password });
  }

  async function signIn(email, password) {
    const c = await ensureClient();
    if (!c) throw new Error('Shared backend is not configured yet.');
    return c.auth.signInWithPassword({ email, password });
  }

  async function signOut() {
    const c = await ensureClient();
    if (!c) return;
    return c.auth.signOut();
  }

  async function saveProfile(profile) {
    const c = await ensureClient();
    if (!c) return { mode: 'local' };
    const { data: { user } } = await c.auth.getUser();
    if (!user) throw new Error('Please sign in first.');
    const row = {
      user_id: user.id,
      full_name: profile.name,
      institution: profile.institution,
      country: profile.country,
      primary_discipline: profile.discipline,
      specializations: profile.specializations,
      methods: profile.methods || null,
      orcid: profile.orcid || null,
      collaboration_interests: profile.interests || null,
      updated_at: new Date().toISOString()
    };
    const { error } = await c.from('profiles').upsert(row, { onConflict: 'user_id' });
    if (error) throw error;
    return { mode: 'shared' };
  }

  async function getMyProfile() {
    const c = await ensureClient();
    if (!c) return { mode: 'local', profile: null };
    const { data: { user } } = await c.auth.getUser();
    if (!user) return { mode: 'shared', profile: null };
    const { data, error } = await c.from('profiles').select('*').eq('user_id', user.id).maybeSingle();
    if (error) throw error;
    return { mode: 'shared', profile: data };
  }

  async function submitIdea(idea) {
    const c = await ensureClient();
    if (!c) return { mode: 'local' };
    const { data: { user } } = await c.auth.getUser();
    if (!user) throw new Error('Please sign in to submit an idea to GDR.');
    const row = {
      submitted_by: user.id,
      title: idea.title,
      primary_domain: idea.domain,
      research_gap: idea.gap,
      multidisciplinary_need: idea.multidisciplinary
    };
    const { data, error } = await c.from('research_ideas').insert(row).select('id').single();
    if (error) throw error;
    return { mode: 'shared', id: data.id };
  }

  return { ensureClient, getSession, signUp, signIn, signOut, saveProfile, getMyProfile, submitIdea };
})();
